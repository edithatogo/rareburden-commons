# Track 013 plan

> Repository-owned review uses the subagent panel under ADR-0008; scientific, equity and patient/community assurance remain separate.

## Phase 1 — Assurance framework

- [x] Define evidence quality, bias and transportability dimensions. `[M-21, S-07]` Evidence: evidence-assessment, transportability and quality-disposition schemas/validators; summary documented in `docs/quality-validation-013-reference.md`.
- [ ] Define validation types, calibration thresholds and model criticism.
- [x] Define release-language rules by evidence maturity. Evidence: `release_language_for_maturity` and negative maturity tests in `cb8bc3d`; policy remains conservative and does not grant external approval.
- [x] Define GATHER-aligned reporting checklist. Evidence: `src/rareburden/reporting.py` and reporting checklist schema.

## Phase 2 — Gap and equity mapping

- [x] Define parameter-by-geography sufficiency taxonomy. `[M-26]` Evidence: gap-map schema uses explicit `sufficiency: not_assessed` until empirical validation.
- [x] Generate machine-readable gap map from source and ledger records. Evidence: `src/rareburden/gapmap.py` and reference gap-map workflow.
- [x] Add rendered coverage, missingness and controlled-data-ask products.
  Evidence: `render_gap_map_markdown`, `tests/test_gapmap.py` and
  `tests/test_gapmap_release_schema.py`; outputs remain metadata-only with
  `sufficiency: not_assessed` until empirical and equity review.
- [ ] Add LMIC, underserved-population and Indigenous governance assessment.

## Phase 3 — Demonstrator validation

- [ ] Triangulate monogenic-diabetes estimates.
- [ ] Triangulate bronchiectasis estimates.
- [ ] Validate paediatric and economic outputs within their permitted scope.
- [ ] Decompose uncertainty and identify decision-sensitive parameters.

## Phase 4 — Independent assurance

- [ ] Run a separately executed owner-operated clean-environment reproduction of at least one analysis. `[S-10]`
- [ ] Complete community/harm agent-panel interpretation review and owner disposition.
- [ ] Complete scientific assurance report and disposition log.
- [ ] Block, narrow or approve outputs for the atlas beta.

## Dependency review — 2026-07-27

- [x] Record that Track 013 cannot activate until Tracks 003, 005, 007, 010, 011 and 012 are complete. Evidence: `c126052`.

## Preparation refresh — 2026-08-01

- [x] Prepare the assurance/equity review packet with validation, triangulation,
  gap, equity, release-language and independent-assurance decisions. Evidence:
  `docs/track-013-assurance-review-packet.md`; prerequisite and external gates
  remain open.
