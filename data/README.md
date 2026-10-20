# Data

Canonical cases: cases-reviewed.json. Generated browser distribution: cases-reviewed.js. Original corpus: audit/original-cases-2026-10-20.json. Screening: case-audit.json and reference-audit.json. Pilot: evidence-pilot.json.

The versioned 1991–2020 NASA POWER baseline is climate_cache.json. Daily provider responses were tested locally. Their public upload is withheld pending approval; climate-raw/README.md explains how to reproduce them locally. Run python3 data/build_climate_cache.py --rebuild-from-raw to reproduce aggregation, using local responses when available and otherwise retrieving public NASA data. Each response has a checksum and provider metadata. See docs/data-method.md.

Run tools/review_cases.py, tools/audit_references.py and tools/finalize_review.py for the case audit pipeline. Candidates never become accepted reference identities automatically.
