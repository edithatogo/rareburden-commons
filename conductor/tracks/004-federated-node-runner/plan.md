# Track 004 plan

## Phase 1 — Node contracts and threat model

- [x] Define input, output, execution-manifest and disclosure-policy schemas. `[M-14, M-18]` Evidence: `schemas/node-execution-manifest.schema.json`, `schemas/node-disclosure-policy.schema.json` and synthetic fixtures.
- [ ] Define trust zones, adversaries, permitted exports and local override rules. `[M-12, M-15]`
- [ ] Define coordinator/node version negotiation and compatibility policy.
- [ ] Obtain data-governance and patient/community review before implementation.

## Phase 2 — Synthetic environment

- [ ] Build synthetic cohort generator with multi-diagnosis and small-cell edge cases. `[C-03]`
- [ ] Implement offline preflight and environment capture. `[M-19]`
- [ ] Implement portable local runner and reproducible package. `[S-08, C-06]`
- [x] Implement disclosure configuration, suppression and export validation. Evidence: `rareburden.node.validate_aggregate_export`, `tests/test_node.py`, and `docs/federated-node-004-reference.md`; custodian-specific thresholds remain external-gated.

## Preparatory implementation — 2026-07-29

- [x] Add a deterministic offline aggregate-export safety boundary that rejects
  participant-level fields and suppresses small cells. Evidence: focused node
  tests and reference documentation.

## Phase 3 — Conformance and security

- [ ] Add contract, privacy, differencing and log-redaction tests.
- [ ] Verify participant rows cannot enter export artefacts. `[M-13]`
- [x] Add node execution manifest contract and fingerprint fields. Evidence: `schemas/node-execution-manifest.schema.json` and synthetic manifest; signing remains release-gated.
- [ ] Test incompatible versions, failed runs, correction and withdrawal.

## Phase 4 — External pilot readiness

- [ ] Write operator, data-steward and export-review guides.
- [ ] Complete independent synthetic-node execution.
- [ ] Prepare controlled-environment pilot protocol and application pack.
- [ ] Complete a pilot before v1 or remove controlled-pilot claims from scope.

## Phase 5 — Review

- [ ] Conduct scientific, privacy, security and engineering review.
- [ ] Record residual risks and required local controls.
- [ ] Release the node alpha only after all blocking findings close.

## Dependency review — 2026-07-27

- [x] Record that Track 004 cannot activate until Tracks 009 and 010 are complete. Evidence: `f919b03`.
