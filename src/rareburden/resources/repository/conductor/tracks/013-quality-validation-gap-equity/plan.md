# Track 013 plan

## Current synthetic sensitivity implementation — 2026-09-05

- [x] Execute baseline and one-parameter-at-a-time model scenarios with
  `rareburden.quality.run_synthetic_model_sensitivity`; retain parameters and
  calculated estimates in the receipt. Relative changes are null for a zero
  baseline or floating-point overflow. Regression evidence:
  `tests/test_track013_synthetic_triangulation.py`.

This implements synthetic diagnostics. Phase 3 retains the broader tasks for
demonstrator validation and uncertainty decomposition.

## Hosted review evidence repair — 2026-09-01

- [x] Retain the current receipt-specific advisory challenge, exact evidence
  bindings and accept/defer options separately from historical output reviews.
  Evidence: `docs/reviews/track-013-receipt-challenge-2026-09-01.yml`.

## Phase 1 — Assurance framework

- [x] Define evidence quality, bias and transportability dimensions. `[M-21, S-07]` Evidence: evidence-assessment, transportability and quality-disposition schemas/validators; summary documented in `docs/quality-validation-013-reference.md`.
- [x] Define validation types, bounded calibration thresholds and model
  criticism. Evidence: `docs/quality-validation-013-protocol.md`.
- [x] Define release-language rules by evidence maturity. Evidence:
  `docs/quality-validation-013-protocol.md`.
- [x] Define GATHER-aligned reporting checklist. Evidence: `src/rareburden/reporting.py` and reporting checklist schema.

## Phase 2 — Gap and equity mapping

- [x] Define parameter-by-geography sufficiency taxonomy. `[M-26]` Evidence: gap-map schema uses explicit `sufficiency: not_assessed` until empirical validation.
- [x] Generate machine-readable gap map from source and ledger records. Evidence: `src/rareburden/gapmap.py` and reference gap-map workflow.
- [x] Add rendered coverage, missingness and conditional controlled-data-ask
  products. Evidence: `docs/track-013-public-data-gap-map-2026-08-21.json` and
  `docs/track-013-public-data-gap-map-2026-08-21.md`.
- [x] Add a role-separated agent assessment of LMIC, underserved-population
  and Indigenous governance risks. Evidence:
  `examples/quality/equity-gap-review-synthetic.yml`; real-population coverage
  and unrelated authority remain conditional external facts.

## Phase 3 — Demonstrator validation

- [x] Triangulate monogenic-diabetes estimates. Evidence:
  `rareburden.demonstrator_validation.execute_monogenic_diabetes_triangulation`,
  `results/track-013-reference-2026-09-06/` and
  `tests/test_demonstrator_validation.py`.
- [x] Triangulate bronchiectasis estimates. Evidence:
  `rareburden.demonstrator_validation.execute_bronchiectasis_triangulation`,
  `results/track-013-reference-2026-09-06/` and
  `tests/test_demonstrator_validation.py`.
- [x] Validate paediatric and economic outputs within their permitted scope. Evidence:
  `rareburden.demonstrator_validation.validate_paediatric_and_economic_scope`,
  `results/track-013-reference-2026-09-06/` and
  `tests/test_demonstrator_validation.py`.
- [x] Decompose uncertainty and identify decision-sensitive parameters. Evidence:
  `rareburden.demonstrator_validation.decompose_uncertainty_and_sensitivity`,
  `results/track-013-reference-2026-09-06/` and
  `tests/test_demonstrator_validation.py`.

## Phase 4 — Owner-operated reproduction and advisory assurance

- [x] Run a separately executed owner-operated reproduction of at least one
  analysis; record it as repository evidence, not independent approval. `[S-10]`
  Evidence reconciled on 2026-09-01:
  `docs/track-013-reproduction-reconciliation-2026-09-01.md` maps the existing
  exact Track 003 synthetic reproduction and advisory output review. No new
  analysis was performed; same-host reproduction is not empirical validation.
- [x] Complete simulated community/harm and interpretation advice without
  claiming lived experience or representation.
- [x] Complete role-separated scientific assurance report and owner disposition.
- [x] Narrow atlas-beta outputs to synthetic and metadata-only assurance until
  empirical dependency evidence exists. Evidence for all three tasks:
  `docs/track-013-agent-assurance-closeout-2026-08-21.yml`.

## Agent-advice closeout — 2026-08-21

- [x] Remove independent-advice and constituted-review requirements; use
  role-separated agent advice plus owner disposition, while retaining external
  evidence only for activated empirical, rights, representation or authority
  claims. Evidence: `docs/decisions/2026-08-21-track-013-agent-advice-boundary.yml`.

## Dependency review — 2026-07-27

- [x] Record that Track 013 cannot activate until Tracks 003, 005, 007, 010, 011 and 012 are complete. Evidence: `c126052`.
