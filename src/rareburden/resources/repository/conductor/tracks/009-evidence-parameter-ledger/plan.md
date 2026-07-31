# Track 009 plan

## Phase 1 — Information model

- [ ] Define parameter, evidence-assessment, assumption and analysis-specification schemas. `[M-03, M-04, M-18]`
- [ ] Define stable IDs, revisions and supersession.
- [ ] Define population, geography, period, measure, metric and unit contracts.
- [ ] Define quality, bias and transportability dimensions. `[M-21, S-07]`

## Phase 2 — Storage and validation

- [ ] Implement ledger read/write/query interfaces.
- [ ] Link parameters to source releases, transformations and semantic entities. `[M-11, M-20]`
- [ ] Enforce mandatory uncertainty, evidence status and licence state. `[M-22]`
- [ ] Add conflict, missingness and incompatible-unit fixtures.

## Phase 3 — Workflow integration

- [ ] Integrate acquisition outputs from Track 002.
- [ ] Build human-readable evidence and assumption reports.
- [x] Add downstream impact tracing for changed parameters. Evidence: `ParameterLedger.impacted_by_source_releases` and regression tests in `4a8c663`; semantic/source-release activation remains gated.
- [ ] Add portable export and schema migration tooling.

## Phase 4 — Review

- [ ] Complete epidemiology, data-governance and engineering review.
- [ ] Validate ledger use with all three demonstrator specifications.
- [ ] Close or assign every blocking data-contract issue.
- [ ] Freeze v0.4 ledger contracts.

## Preparatory repository implementation — 2026-07-31

- [x] Add a transactional append-only reference store for validated ledger
  snapshots with sequential revisions, immutable triggers, canonical content
  hashes, chain verification and atomic JSONL export. Evidence:
  `rareburden.ledger_store`, `tests/test_ledger_store.py` and
  `docs/evidence-ledger-009-reference.md`. Custodian authority and signed
  checkpoints remain external gates.
- [x] Add bounded read/query and detached portable-export interfaces. Evidence:
  `ParameterLedger.query`, `ParameterLedger.portable_document` and focused
  mutation-isolation tests.
- [x] Add fail-closed population/period compatibility checks and unsupported
  migration rejection. Evidence: `ParameterLedger.require_compatible_context`,
  `migrate_ledger_document` and focused negative tests. The versioned v0.4
  migration design remains approval-gated.

## Dependency review — 2026-07-27

- [x] Record that Track 009 cannot activate until Tracks 002 and 008 are complete. Evidence: `ebca9a1`.
- [x] Add non-binding ledger contract v0.1.0 draft to the specification; activation and contract freeze remain blocked.
