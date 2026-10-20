# Research tools

- review_cases.py: applies documented qualitative corrections to the preserved original corpus and constructs the evidence pilot.
- audit_references.py: retrieves Crossref search leads without accepting them as verified identities.
- finalize_review.py: generates browser case data and human-readable audit tables.
- test_research.js: checks corpus integrity, missing-data calculations, units, baseline coverage and JavaScript syntax.
- test_climate.py: independently checks archived responses, checksums and aggregation.

From repository root: node tools/test_research.js and python3 tools/test_climate.py. Climate rebuilding is documented in data/README.md.
