# Claim-level evidence protocol

Version 1.0, 20 October 2026. The unit of assessment is one pressure–response claim. Contributor origin, a bibliography entry, the age of a practice and a photograph do not determine evidence strength. Whole-case A–D grades are retired.

## Fields

Each response has a stable `SHIFT-NNN-RNN` ID, pressure, mechanism, strategy family, arrangement and effect, plus:

| Field | Meaning |
|---|---|
| type | measured, simulated, documented_design, documented_use, mechanism_inference or unknown |
| status | qualitative_interpretation, metadata_verified, full_text_reviewed or verification_pending |
| site_relation | Same object, comparable building/type, generic mechanism or unknown; specify the actual relation |
| source_ids / locator | Reference IDs plus page, figure, table, section or dated field record; empty means verification is missing |
| outcome | Specific variable or documented fact; distinguish air, surface, mean radiant and operative temperature |
| value / unit | Source-specific quantity and unit, or null for an unquantified result; null is not zero |
| comparator | Reference condition, with proposed comparisons explicitly identified as proposals |
| conditions | Weather, geometry, construction, occupancy, operation and dates |
| limitations | Confounding, transfer constraints and missing support |
| reviewed_at | Editorial screening date |

Evidence type is descriptive, not a ranking. Interviews can document operation without measuring insulation. Simulation can quantify a scenario without establishing historical use. A measurement in a comparable building remains comparable-building evidence.

## Review sequence

1. Identify the object, point precision and exact claim.
2. Verify source identity. Automated bibliographic candidates are only leads.
3. Inspect the source/record and record the exact locator.
4. Extract outcome, comparator, conditions, method and uncertainty.
5. Separate source findings from editorial interpretation.
6. Retain numerical values only with defensible provenance, units and scope.
7. Record unresolved checks. Explicit qualitative interpretation remains publishable when measurement is missing.

Historical and community-specific interpretations require traceable evidence separately. Regional climate data do not validate building performance. Image subject, rights and relation to the mapped site also require separate verification.

## Pilot

Cases **4, 5, 6, 7, 12, 34, 37, 38, 40, 42, 53 and 57** cover courtyards, mass/ground coupling, air paths, screens, body-scale shelter, seasonal insulation and a contemporary demonstrator. Selection is purposive, not representative.

The **43 pilot rows** expose outcomes, conditions and limitations. A qualitative trullo finding links to inspected measurements of a **comparable Fasano building**, not the mapped Alberobello point. Cartuja Qanat rows link to inspected **project design documentation**, not measured cooling performance. Other rows remain physical interpretations with missing claim-level locators. This pilots evidence representation; it does not certify twelve measured cases.

Use the same Response ID in the partner template's Responses and Evidence tabs. Keep reference IDs/locators in Responses, and location relationship, outcome, value/unit, comparator, conditions, verification status and limitations in Evidence. Leave numerical fields blank when no supported value exists. Editors verify before publication; automatic publishing is not introduced.

## Mechanism coding

Published row mechanisms and strategy families are explicit editorial assignments. Original explicit labels are retained where appropriate; other rows use documented case/row mappings. No substring classifier assigns published mechanisms. These labels describe interpretations and do not add performance evidence.
