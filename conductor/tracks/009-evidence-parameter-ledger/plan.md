# Track 009 plan

> Repository-owned review uses the subagent panel under ADR-0008; scientific and custodian evidence decisions remain separate.

## Phase 1 — Information model

- [x] Define parameter, evidence-assessment, assumption and analysis-specification schemas. `[M-03, M-04, M-18]` Evidence: the four JSON Schemas, strict schema collection validation and synthetic fixtures; contracts remain non-binding pending review.
- [x] Define stable IDs, revisions and supersession. Evidence: parameter IDs/fingerprints, required positive revisions, supersession invariants and durable sequential snapshot receipts.
- [x] Define population, geography, period, measure, metric and unit contracts. Evidence: required strict population/period objects, date/age ordering invariants and unit/quantity tests.
- [x] Define quality, bias and transportability dimensions. `[M-21, S-07]` Evidence: evidence- and transportability-assessment schemas and validated synthetic assessments; external methods review remains open.

## Phase 2 — Storage and validation

- [x] Implement ledger read/write/query interfaces. Evidence: validated loading, bounded queries, detached export and transactional durable snapshots.
- [x] Link parameters to source releases, transformations and semantic entities. `[M-11, M-20]` Evidence: required source-release, transformation and semantic-entity ID fields in the parameter contract and fixture.
- [x] Enforce mandatory uncertainty, evidence status and licence state. `[M-22]` Evidence: required enumerated schema fields, distribution invariants and assumed/non-assumed provenance checks.
- [x] Add conflict, missingness and incompatible-unit/context fixtures. Evidence: explicit alternative conflict grouping, missing provenance/context failures and model unit/period/population negative tests; no automatic conflict selection.

## Phase 3 — Workflow integration

- [x] Integrate acquisition outputs from Track 002. Evidence: `validate_source_release_links` resolves every referenced release and fails closed on missing or unusable licence states; live-source approval remains Track 002-gated.
- [x] Build human-readable evidence and assumption reports. Evidence: deterministic `ParameterLedger.render_markdown` with separate evidence/assumption sections, provenance, uncertainty, licence and limitations coverage.
- [x] Add downstream impact tracing for changed parameters. Evidence: `ParameterLedger.impacted_by_source_releases` and regression tests in `4a8c663`; semantic/source-release activation remains gated.
- [x] Add portable export and schema migration tooling. Evidence: canonical JSONL history export and fail-closed `migrate_ledger_document`; future migrations remain approval-gated.

## Phase 4 — Review

- [ ] Complete epidemiology, data-governance and engineering review.
- [x] Validate ledger use with all three demonstrator specifications. Evidence:
  schema-validated non-binding profiles for RBC-P002, RBC-P003 and RBC-P004,
  plus fail-closed binding checks in `rareburden.demonstrator_readiness`. The
  profiles deliberately report unresolved scientific and controlled-data roles
  and therefore do not declare any demonstrator analysis ready.
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

## Preparation refresh — 2026-08-01

- [x] Prepare the ledger review packet with evidence lanes, freeze decisions,
  migration requirements and custody boundaries. Evidence:
  `docs/track-009-ledger-review-packet.md`; upstream source/semantic and
  external epidemiology/data-governance/engineering review remain open.
