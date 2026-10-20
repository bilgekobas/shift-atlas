"""Independent raw-data checks for units, coverage, aggregation and provenance."""
import calendar
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'data/build_climate_cache.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
snap=json.loads((ROOT/'data/climate_cache.json').read_text())
checked=0
for key,out in snap['locations'].items():
 archive=ROOT/'data/climate-raw'/f'{key}.json.gz'
 if not archive.exists():
  continue
 raw=gzip.decompress(archive.read_bytes())
 assert hashlib.sha256(raw).hexdigest()==out['provenance']['response_sha256']
 data=json.loads(raw);p=data['properties']['parameter']
 for m in range(1,13):
  pr=[v for d,v in p['PRECTOTCORR'].items() if int(d[4:6])==m]
  sr=[v for d,v in p['ALLSKY_SFC_SW_DWN'].items() if int(d[4:6])==m]
  expected=sum(calendar.monthrange(y,m)[1] for y in range(1991,2021))
  assert len(pr)==expected and len(sr)==expected
  assert abs(sum(pr)/30-out['prec'][m-1])<=.00051
  assert abs(sum(sr)/30-out['sr'][m-1])<=.00051
  assert abs(sum(sr)/expected-out['srDaily'][m-1])<=.00051
 checked+=1
# A missing precipitation or irradiation day cannot become a valid zero month.
d={'time':['1991-01-01'],'temperature_2m_max':[0],'temperature_2m_min':[0],
   'temperature_2m_mean':[0],'precipitation_sum':[0],'shortwave_radiation_sum':[3.6]}
assert b.monthly_from_daily(d,{'shortwave_radiation_sum':'MJ/m²'})['prec'][0] is None
assert b.monthly_from_daily(d,{'shortwave_radiation_sum':'MJ/m²'})['sr'][0] is None
print(f'PASS: {checked}/{len(snap["locations"])} available raw-response checksums and aggregations; missing-day handling.')
if checked<len(snap['locations']):
 print('RAW CHECKS INCOMPLETE: daily binaries are withheld from publication; run the builder to acquire them locally. Snapshot/schema and summary checks remain in test_research.js.')
