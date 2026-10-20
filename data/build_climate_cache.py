"""Build the reproducible NASA POWER 1991–2020 atlas snapshot (stdlib only).

Run from repository root: python3 data/build_climate_cache.py
Requires data/cases-reviewed.json. Progress is checkpointed after each location.
"""
import calendar
import concurrent.futures
import hashlib
import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START, END, MODEL = '1991-01-01', '2020-12-31', 'nasa_power'
VARIABLES = ['temperature_2m_max', 'temperature_2m_min', 'temperature_2m_mean',
             'precipitation_sum', 'shortwave_radiation_sum',
             'relative_humidity_2m_mean', 'dew_point_2m_mean']
SCHEMA = 'shift-climate-v2'


def monthly_from_daily(daily, units):
    sr_unit = units.get('shortwave_radiation_sum')
    if sr_unit not in ('MJ/m²', 'kW-hr/m^2/day'):
        raise ValueError('Unexpected radiation units')
    dates = daily['time']
    expected = [sum(calendar.monthrange(y, m + 1)[1] for y in range(1991, 2021)) for m in range(12)]
    buckets = {k: [[] for _ in range(12)] for k in ['tmax', 'tmin', 'tmean', 'prec', 'ah', 'sr', 'rh']}
    for i, date in enumerate(dates):
        m = int(date[5:7]) - 1
        def value(k):
            a = daily.get(k, [])
            return a[i] if i < len(a) and a[i] is not None and math.isfinite(a[i]) else None
        for out, src in [('tmax', 'temperature_2m_max'), ('tmin', 'temperature_2m_min'),
                         ('tmean', 'temperature_2m_mean'), ('prec', 'precipitation_sum'),
                         ('rh', 'relative_humidity_2m_mean')]:
            v = value(src)
            if v is not None:
                buckets[out][m].append(v)
        sr = value('shortwave_radiation_sum')
        if sr is not None:
            buckets['sr'][m].append(sr / 3.6 if sr_unit == 'MJ/m²' else sr)
        td, t = value('dew_point_2m_mean'), value('temperature_2m_mean')
        if td is not None and t is not None:
            e = 6.112 * math.exp(17.67 * td / (td + 243.5))
            buckets['ah'][m].append(216.7 * e / (t + 273.15))
    out = {'coverage': {}, 'srDaily': []}
    for k, months in buckets.items():
        out['coverage'][k] = [len(a) / expected[m] for m, a in enumerate(months)]
        # Require complete daily coverage: missing days never become zero precipitation/radiation.
        out[k] = [round(sum(a) / (30 if k in ('prec', 'sr') else len(a)), 3)
                  if len(a) == expected[m] else None for m, a in enumerate(months)]
    out['srDaily'] = [round(sum(a) / len(a), 3) if len(a) == expected[m] else None
                      for m, a in enumerate(buckets['sr'])]
    return out


def fetch_location(c):
    lat, lon = c['coords']
    params = {'latitude': f'{lat:.3f}', 'longitude': f'{lon:.3f}', 'start': '19910101',
              'end': '20201231', 'parameters': 'T2M_MAX,T2M_MIN,T2M,T2MDEW,PRECTOTCORR,ALLSKY_SFC_SW_DWN',
              'community': 'RE', 'format': 'JSON', 'time-standard': 'UTC'}
    url = 'https://power.larc.nasa.gov/api/temporal/daily/point?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'ShiftAtlasResearch/2.0'})
    import gzip
    raw_dir = ROOT / 'data/climate-raw'
    raw_dir.mkdir(exist_ok=True)
    raw_path = raw_dir / f'{lat:.3f},{lon:.3f}.json.gz'
    from_archive = raw_path.exists()
    raw = gzip.decompress(raw_path.read_bytes()) if from_archive else urllib.request.urlopen(req, timeout=60).read()
    d = json.loads(raw)
    if d['header']['time_standard'] != 'UTC':
        raise ValueError('Unexpected time standard')
    values = d['properties']['parameter']
    dates = sorted(values['T2M'])
    daily = {'time': [f'{v[:4]}-{v[4:6]}-{v[6:]}' for v in dates]}
    mapping = {'temperature_2m_max': 'T2M_MAX', 'temperature_2m_min': 'T2M_MIN',
               'temperature_2m_mean': 'T2M', 'dew_point_2m_mean': 'T2MDEW',
               'precipitation_sum': 'PRECTOTCORR', 'shortwave_radiation_sum': 'ALLSKY_SFC_SW_DWN'}
    units = {}
    for key, src in mapping.items():
        daily[key] = [values[src].get(v) if values[src].get(v) != d['header']['fill_value'] else None for v in dates]
        units[key] = d['parameters'][src]['units']
    result = monthly_from_daily(daily, units)
    result['provenance'] = {'provider': 'NASA POWER', 'request_url': url, 'start_date': START,
        'end_date': END, 'requested_coordinates': [lat, lon],
        'response_point_coordinates': d['geometry']['coordinates'],
        'point_note': 'Response point is not an independently located building or native grid-cell centre.',
        'meteorology': 'MERRA-2; native grid 0.5° latitude × 0.625° longitude',
        'solar': 'POWER SRB/CERES solar products; coarser grid, approximately 1°',
        'retrieved_at': None if from_archive else datetime.now(timezone.utc).isoformat(),
        'aggregation_source': 'archived_response' if from_archive else 'provider_request',
        'response_sha256': hashlib.sha256(raw).hexdigest(),
        'api_header': d['header'], 'input_units': units, 'days': len(dates)}
    # Archive response bytes locally so rebuilding statistics does not require another request.
    if not from_archive:
        import os
        tmp_path = raw_path.with_suffix('.tmp')
        tmp_path.write_bytes(gzip.compress(raw, mtime=0))
        if hashlib.sha256(gzip.decompress(tmp_path.read_bytes())).hexdigest() != hashlib.sha256(raw).hexdigest():
            raise ValueError('Archive verification failed')
        os.replace(tmp_path, raw_path)
    return f'{lat:.3f},{lon:.3f}', result


def main():
    cases = json.loads((ROOT / 'data/cases-reviewed.json').read_text())
    path = ROOT / 'data/climate_cache.json'
    previous = json.loads(path.read_text()) if path.exists() else {}
    import sys
    locations = previous.get('locations', {}) if '--rebuild-from-raw' not in sys.argv and previous.get('schema_version') == SCHEMA and previous.get('model') == MODEL else {}
    unique = {f'{c["coords"][0]:.3f},{c["coords"][1]:.3f}': c for c in cases}
    pending = [c for key, c in unique.items() if key not in locations]
    def safe(c):
        try:
            return c, fetch_location(c), None
        except Exception as e:
            return c, None, f'{type(e).__name__}: {e}'
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
      for c, fetched, error in pool.map(safe, pending):
        if error:
            print(c['name'] + ': ' + error, flush=True)
            continue
        key, result = fetched
        if result:
            if result['provenance']['retrieved_at'] is None:
                prior_prov = previous.get('locations', {}).get(key, {}).get('provenance', {})
                if prior_prov.get('response_sha256') == result['provenance']['response_sha256']:
                    result['provenance']['retrieved_at'] = prior_prov.get('retrieved_at')
            locations[key] = result
            snapshot = {'schema_version': SCHEMA, 'generated': datetime.now(timezone.utc).isoformat(),
                'baseline': '1991–2020 NASA POWER; MERRA-2 meteorology and SRB/CERES solar products; UTC days',
                'model': MODEL, 'start_date': START, 'end_date': END,
                'units': {'tmax': '°C (mean daily maximum)', 'tmin': '°C (mean daily minimum)',
                    'tmean': '°C (mean daily mean)', 'prec': 'mm/month', 'rh': '%',
                    'ah': 'g/m³ (estimate from daily mean dew point and temperature)',
                    'sr': 'kWh/m²/month', 'srDaily': 'kWh/m²/day'},
                'limitations': ['Regional reanalysis does not describe building microclimate.',
                    'Absolute humidity is estimated from daily mean inputs, not averaged hourly absolute humidity.',
                    'Monthly values require complete daily coverage. No building comfort or heat-stress inference is made.'],
                'locations': locations}
            path.write_text(json.dumps(snapshot, ensure_ascii=False, separators=(',', ':')))
            print(f'{len(locations)} {c["name"]}: OK', flush=True)


if __name__ == '__main__':
    main()
