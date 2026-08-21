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

- [x] Complete role-separated epidemiology, rights/data-use and engineering
  agent-panel review and owner disposition for the bounded synthetic candidate.
  Evidence: `docs/track-009-bounded-agent-challenge-2026-08-16.yml`,
  `docs/decisions/2026-08-21-track-009-post-merge-options.yml` and
  `docs/decisions/2026-08-22-track-009-agent-owner-closeout.yml`. Agent advice
  is not independent review or external approval.
- [x] Validate ledger use with all three demonstrator specifications. Evidence:
  schema-validated non-binding profiles for RBC-P002, RBC-P003 and RBC-P004,
  plus fail-closed binding checks in `rareburden.demonstrator_readiness`. The
  profiles deliberately report unresolved scientific and controlled-data roles
  and therefore do not declare any demonstrator analysis ready.
- [x] Assign every blocking data-contract issue to an accountable role while
  retaining pending status until exact-candidate evidence exists. Evidence:
  `docs/track-009-freeze-readiness-2026-08-21.yml`; assignment does not resolve
  the three findings or confer epidemiology/data-governance approval.
- [ ] Freeze v0.4 ledger contracts.

## Preparation refresh — 2026-08-02

- [x] Add a negative regression for empty supersession receipts and retain
  deterministic migration evidence. Evidence: `test_ledger_model.py`; this
  strengthens the fail-closed contract without activating the ledger.

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

## Bounded source-ledger reconciliation — 2026-08-16

- [x] Bind the ledger source register to the immutable Track 008 inventory
  fingerprint and current Track 002 evidence receipts, with distinct licence,
  visibility and activation states. Evidence:
  `docs/track-009-source-release-bindings-2026-08-16.yml` and
  `manifests/ledger/track-009-source-release-bindings-2026-08-16.json`.
- [x] Reject private, disabled, unusable-licence or mutable source-release links
  before a parameter can be used. Evidence: `ParameterLedger` validation and
  positive/negative tests in `tests/test_ledger.py` and
  `tests/test_track009_source_bindings.py`.
- [x] Require explicit rationale when selecting among a complete alternative
  parameter set; never auto-select a conflict. Evidence:
  `ParameterLedger.select_alternative` and focused tests.
- [x] Run bounded repository epidemiology, rights and engineering agent
  challenge. Evidence: `docs/track-009-bounded-agent-challenge-2026-08-16.yml`.
  Three medium findings remain controlled by disabled empirical activation.
- [x] Record owner disposition and repeat the bounded challenge after Track 008
  completion. Evidence: `docs/decisions/2026-08-22-track-009-agent-owner-closeout.yml`.
  The three medium findings remain pending and the v0.4 ledger contract is not
  frozen.

## Option B preparation control — 2026-08-20

- [x] Enforce provisional ledger preparation without allowing Track 009 to
  activate before Track 008 completes. Evidence:
  `docs/downstream-bounded-preparation-plan-2026-08-03.yml`,
  `scripts/check_downstream_preparation.py` and focused out-of-order activation
  tests. Epidemiology, rights/data-use, engineering and contract-freeze gates
  remain open.

## Freeze-readiness control — 2026-08-21

- [x] Encode and machine-enforce the dependency, ledger-review, assigned
  data-contract issue, exact-candidate migration and v0.4 freeze evidence
  required for Track 009 closure. Evidence:
  `docs/track-009-freeze-readiness-2026-08-21.yml`,
  `scripts/check_track_009_freeze_readiness.py` and focused negative tests.
  Track 009 remains blocked and all accountable review/freeze tasks stay open.

## Post-Track 008 bounded-freeze reconciliation — 2026-08-21

- [x] Bind Track 009's dormant synthetic preparation to the exact bounded
  Track 008 candidate, owner decision and readiness hashes while retaining the
  declared completion dependency as unsatisfied. Evidence:
  `docs/decisions/2026-08-21-track-009-post-track-008-reconciliation.yml` and
  `docs/track-009-freeze-readiness-2026-08-21.yml`. Track 009 remains blocked,
  inactive and unfrozen; the agent panel is advisory and the owner's
  disposition authorizes reversible preparation only.
- [x] Generate deterministic JSON exports for both synthetic ledgers and bind
  their schema, inputs, outputs and self-baseline migration receipt in an exact
  provisional candidate manifest. Evidence:
  `manifests/ledger/track-009-v0.4-candidate-2026-08-21.json`,
  `manifests/ledger/track-009-v0.4-migration-impact-2026-08-21.json` and
  `scripts/build_track009_v04_candidate.py`. This is review preparation only;
  empirical activation, accountable reviews and the v0.4 ledger freeze remain
  false or pending.

## Review fixes — 2026-08-21

- [x] Emit candidate JSON as explicit UTF-8 bytes with LF line endings so
  deterministic regeneration produces identical evidence on Windows, macOS
  and Linux. Evidence: hosted Windows portability finding and the candidate
  builder reproducibility test.

## Exact post-merge advisory preparation — 2026-08-21

- [x] Bind a schema-valid, role-separated advisory packet to the exact merged
  Track 009 candidate and retain the owner decision as pending. Evidence:
  `docs/decisions/2026-08-21-track-009-post-merge-options.yml`. The panel is
  simulated and advisory; it is not independent review or owner disposition.
- [x] Add fail-closed containment validation for the exact candidate commit,
  tree, manifest, synthetic input/export allowlist, source identifiers,
  semantic identifiers and non-empirical warnings. Evidence:
  `scripts/check_track009_candidate_containment.py` and focused negative tests.
  Track 009 remains blocked, inactive, incomplete and unfrozen; Track 010
  remains ineligible.
- [x] Record the repository owner's explicit selection of recommended Option A
  against the exact merged candidate and bind its receipt hash into freeze
  readiness and containment validation. This owner-operated disposition permits
  reversible synthetic preparation and containment only; it is not independent
  review and does not satisfy any review, activation, freeze or release gate.

## Operational regeneration assurance — 2026-08-21

- [x] Make the operational containment gate regenerate the two synthetic ledger
  exports, migration receipt and candidate manifest twice in isolated temporary
  roots and require byte equality with each other and the hash-bound checked-in
  candidate. Evidence: `scripts/check_track009_candidate_containment.py` and
  `tests/test_track009_candidate_containment.py`. This demonstrates bounded
  same-process, same-environment repository reproducibility only, not an
  independent clean-install or cross-environment reproduction. Equality does
  not validate estimands, denominators, uncertainty calibration or propagation,
  model correctness, source fitness or real-data reproducibility. Track 009
  remains blocked, synthetic-only, provisional and unfrozen, and it creates no
  empirical, rights, review or Track 010 eligibility claim.

## Synthetic source-to-profile-role structural check — 2026-08-21

- [x] Add a provisional source-to-bound-profile-role structural schema, an exact matrix
  for every currently bound synthetic demonstrator-profile role, and a
  fail-closed validator. Evidence:
  `schemas/source-profile-role-structural-assessment.schema.json`,
  `examples/ledger/source-profile-role-structural-synthetic.yml`,
  `scripts/check_track009_source_profile_role.py` and focused negative
  tests. The matrix rejects the generic population count as a monogenic-diabetes
  or bronchiectasis disease denominator and leaves both the assumed aetiologic
  fraction and paediatric all-residents context unassessed. No target estimand
  is defined by the non-binding profiles. This exercises but does not
  resolve EPI-MED-01/02; empirical fitness, rights, review, freeze and Track 010
  eligibility remain blocked.

## Bounded agent-owner review closeout — 2026-08-22

- [x] Reconcile the completed Track 008 bounded dependency, rerun the
  role-separated epidemiology, rights/data-use and engineering challenge, and
  record the owner's disposition. Evidence:
  `docs/decisions/2026-08-22-track-009-agent-owner-closeout.yml`.
- [ ] Freeze v0.4 ledger contracts. Exact estimand fitness, rights/custody,
  engineering review findings and release evidence remain pending.
