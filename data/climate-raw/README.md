# Daily source archive

The atlas publishes monthly climate summaries and per-location NASA request URLs, input units, provider metadata and source-response checksums in `../climate_cache.json`.

The 57 compressed daily NASA POWER responses were inspected and tested locally. Publication of those large binary archives is currently withheld pending explicit approval after automatic approval review rejected their upload. They are not included in this repository version. This does not affect the published monthly climate layer.

Run `python3 data/build_climate_cache.py --rebuild-from-raw` from the repository root to obtain missing daily responses from the public NASA URLs and reproduce the aggregation locally. The builder reuses valid local archives. NASA response timing metadata can change, so a fresh response may have a different byte checksum even when its climate series are identical.
