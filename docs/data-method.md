# Climate data and methods

Version 2.0, 20 October 2026.

## Baseline and spatial meaning

The published snapshot covers **1 January 1991–31 December 2020**, using the NASA POWER Daily API, community RE, with UTC days explicitly requested. Meteorology uses MERRA-2. Solar data use POWER SRB/CERES products, including a source transition during the period. This is regional climate context, not a station normal or a measurement of the building.

The ERA5 download through Open-Meteo was rate-limited. All published locations instead use POWER consistently; the partial ERA5 series is not mixed into this baseline. The old 2019–2023 cache and browser caches are not used.

Native meteorological resolution is about 0.5° latitude × 0.625° longitude; solar resolution is coarser, approximately 1°. Courtyard conditions, street shade, coastal contrasts, islands and highland topography are unresolved. Returned point/elevation metadata do not independently establish a building location or native grid-cell centre. Decimal precision is not survey accuracy.

## Inputs and aggregation

| Parameter | Daily input | Monthly output |
|---|---|---|
| T2M_MAX | Maximum 2 m temperature, °C | Mean daily maximum in that calendar month |
| T2M_MIN | Minimum 2 m temperature, °C | Mean daily minimum |
| T2M | Mean 2 m temperature, °C | Mean daily mean |
| T2MDEW | Mean dew/frost point, °C | Input to estimated absolute humidity |
| PRECTOTCORR | Corrected precipitation, mm/day | Calendar-month sum divided by 30 years |
| ALLSKY_SFC_SW_DWN | Daily irradiation, kWh/m²/day | Calendar-month sum divided by 30 years |

Annual precipitation/irradiation sum all twelve monthly totals. `srDaily` separately stores mean daily irradiation by month. Daily and monthly irradiation are not interchangeable. The mean monthly min–max statistic averages twelve monthly values; the daily-range statistic is descriptive, not heat stress.

For MJ/m² inputs, **kWh/m² = MJ/m² ÷ 3.6**. POWER already supplies kWh/m²/day; no additional conversion applies.

Absolute humidity is estimated as `216.7 × e / (T + 273.15)`, where `e = 6.112 × exp(17.67 × Td / (Td + 243.5))`, e is hPa, and T/Td are daily mean temperature/dew point in °C. Using daily means in this nonlinear expression approximates, rather than reproduces, an hourly-derived average. It does not establish dehumidification need, comfort or evaporative-cooling performance.

## Missing values and reproducibility

Provider fill values become null. Each variable/month requires all expected daily values for the 30-year window; any missing day makes that monthly value unavailable. Annual totals and twelve-month means require twelve finite months. A measured zero remains zero.

Each location records request URL, period, units, native resolution, provider/API metadata, retrieval time and response SHA-256. Compressed source responses were checked locally; their public upload is withheld pending explicit approval. They are not included in this repository version. The public snapshot retains NASA URLs, units and response checksums. The builder can retrieve responses for local reproduction; provider timing metadata may change a response checksum without changing the climate series. `data/build_climate_cache.py` reconstructs statistics, and `data/climate-tools.js` owns displayed summaries. No unversioned localStorage or changing live weather is used.

## Comfort, projections and analogues

The outdoor comparison with an indoor adaptive-comfort band is removed. Monthly regional weather cannot establish indoor operative temperature, comfort hours, physiological heat stress or a building strategy's effectiveness.

The five zone-level future offsets, CMIP6 ensemble attribution and analogue scores are withdrawn. Future outputs require traceable models, scenarios, reference/target periods, location extraction, ensemble spread, bias treatment and uncertainty. Analogue matching additionally requires explicit features, candidate coverage, missing-data policy, covariance treatment, seasonal alignment and sensitivity/validation checks. Neither projections nor rankings are currently published.

## Primary methodological sources

- NASA POWER meteorology: https://power.larc.nasa.gov/docs/methodology/meteorology/
- NASA POWER Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- NASA POWER Monthly API/source periods: https://power.larc.nasa.gov/docs/services/api/temporal/monthly/
- WMO climatological normals: https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/climate-services/wmo-climatological-normals
- CBE comfort applicability: https://comfort.cbe.berkeley.edu/
- Fitzpatrick & Dunn (2019), an analogue reference, not validation of the retired atlas calculation: https://doi.org/10.1038/s41467-019-08540-3
- Open-Meteo historical API and units: https://open-meteo.com/en/docs/historical-weather-api
