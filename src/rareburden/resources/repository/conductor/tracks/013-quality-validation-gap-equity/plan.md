# Track 013 plan

## Phase 1 — Assurance framework

- [x] Define evidence quality, bias and transportability dimensions. `[M-21, S-07]` Evidence: evidence-assessment, transportability and quality-disposition schemas/validators; summary documented in `docs/quality-validation-013-reference.md`.
- [x] Define validation types, calibration thresholds and model criticism. Evidence: repository-owned draft in `docs/quality-validation-013-protocol.md`; empirical calibration remains open.
- [x] Define release-language rules by evidence maturity. Evidence: maturity/language matrix in `docs/quality-validation-013-protocol.md`; approval and release disposition remain open.
- [x] Define GATHER-aligned reporting checklist. Evidence: `src/rareburden/reporting.py` and reporting checklist schema.

## Phase 2 — Gap and equity mapping

- [x] Define parameter-by-geography sufficiency taxonomy. `[M-26]` Evidence: gap-map schema uses explicit `sufficiency: not_assessed` until empirical validation.
- [x] Generate machine-readable gap map from source and ledger records. Evidence: `src/rareburden/gapmap.py` and reference gap-map workflow.
- [ ] Add rendered coverage, missingness and controlled-data-ask products.
- [ ] Add LMIC, underserved-population and Indigenous governance assessment.

## Phase 3 — Demonstrator validation

- [ ] Triangulate monogenic-diabetes estimates.
- [ ] Triangulate bronchiectasis estimates.
- [ ] Validate paediatric and economic outputs within their permitted scope.
- [ ] Decompose uncertainty and identify decision-sensitive parameters.

## Phase 4 — Independent assurance

- [ ] Commission independent reproduction of at least one analysis. `[S-10]`
- [ ] Complete patient/community harm and interpretation review.
- [ ] Complete scientific assurance report and disposition log.
- [ ] Block, narrow or approve outputs for the atlas beta.

## Dependency review — 2026-07-27

- [x] Record that Track 013 cannot activate until Tracks 003, 005, 007, 010, 011 and 012 are complete. Evidence: `c126052`.
