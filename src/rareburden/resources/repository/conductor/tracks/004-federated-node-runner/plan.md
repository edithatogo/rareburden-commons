# Track 004 plan

## Phase 1 — Node contracts and threat model

- [x] Define input, output, execution-manifest and disclosure-policy schemas. `[M-14, M-18]` Evidence: four `schemas/node-*.schema.json` contracts and schema-valid synthetic fixtures.
- [x] Define trust zones, adversaries, permitted exports and local override rules. `[M-12, M-15]` Evidence: `docs/federated-node-004-threat-model.md`; controlled governance approval remains open.
- [x] Define coordinator/node version negotiation and compatibility policy. Evidence: major-version helper and threat-model boundary; release compatibility policy remains review-gated.
- [x] Define coordinator/node major-version compatibility and execution-manifest creation. Evidence: `rareburden.node` helpers and tests; full negotiation policy remains review-gated.
- [ ] Obtain data-governance and patient/community review before controlled-data implementation or pilot activation.

## Phase 2 — Synthetic environment

- [x] Build deterministic aggregate-only synthetic cohort generator with multi-diagnosis and small-cell edge cases. `[C-03]` Evidence: `build_synthetic_cohort` and deterministic fixture tests; no participant identifiers.
- [x] Add a deterministic offline synthetic node runner over supplied rows. Evidence: `rareburden.node.run_offline_node` and focused positive/negative tests; no persistence, network access, or controlled data.
- [x] Implement offline preflight and bounded environment capture. `[M-19]` Evidence: `build_execution_manifest`, `capture_environment`, and focused tests; capture is limited to runtime identity plus a caller-supplied lockfile fingerprint, with no credentials, host paths, or participant data.
- [x] Implement deterministic offline execution-manifest preflight. `[M-19]` Evidence: `build_execution_manifest`, `capture_environment`, and version/environment tests; controlled-node execution remains pending external authorization.
- [x] Package and exercise the bounded synthetic aggregate validator from an installed wheel. `[S-08, C-06]` Evidence: package checks, installed-wheel node execution and `scripts/check_node_reproducibility.py`.
- [x] Implement a bounded synthetic common-analysis runner and deterministic local-only wheel-bundle builder. Evidence: `rareburden.node_analysis`, `scripts/build_node_bundle.py`, focused negative tests and installed-wheel execution. The runner accepts only explicitly synthetic records; the bundle builder downloads nothing and requires pre-staged wheels.
- [ ] Approve the production common analysis contract and stage a complete locked dependency wheel set after Tracks 009/010 and policy approval.
- [x] Rehearse a complete current-platform candidate wheelhouse and clean
  network-disabled installation. Evidence:
  `scripts/check_offline_node_install.py`,
  `docs/federated-node-004-offline-install-rehearsal.md` and focused command/
  failure tests. Cross-platform staging, dependency approval and independent
  operation remain open.
- [x] Implement disclosure configuration, suppression and export validation. Evidence: `rareburden.node.validate_aggregate_export`, `tests/test_node.py`, and `docs/federated-node-004-reference.md`; custodian-specific thresholds remain external-gated.

## Preparatory implementation — 2026-07-29

- [x] Add a deterministic offline aggregate-export safety boundary that rejects
  participant-level fields and suppresses small cells. Evidence: focused node
  tests and reference documentation.

## Phase 3 — Conformance and security

- [x] Add contract, privacy, supplied-history query-budget and log-redaction tests. Evidence: allowlisted aggregate dimensions, monotonic threshold comparisons, bounded query-history guards, recursive credential redaction and adversarial tests.
- [x] Implement immutable synthetic policy snapshots, stable value-free query-shape identity, replay rejection and overlap-budget checks. Evidence: `rareburden.node_policy` and focused tests.
- [ ] Bind the policy and query ledger to an authoritative custodian-controlled durable store in the approved runner; the in-memory snapshots do not establish authority or persistence.
- [x] Verify participant rows cannot enter export artefacts. `[M-13]` Evidence: case-normalised sensitive-field rejection, nested-value rejection, aggregate dimension allowlist and offline-runner tests.
- [x] Add node execution manifest contract and fingerprint fields. Evidence: strict digest schema, canonical output hash and tamper-evident manifest tests.
- [ ] Obtain signing/attestation design approval and implement the approved trust-root/key-custody profile. Local output hashes are implemented; signing authority is external-gated with Track 016.
- [x] Prepare a non-binding signing/attestation decision packet with trust-model
  options, a recommendation and exact closure evidence. Evidence:
  `docs/federated-node-004-signing-decision-packet.md`; this does not approve or
  implement a production trust root.
- [x] Add a schema-validated cross-platform wheelhouse verification matrix that
  distinguishes same-operator candidates from independent approved receipts.
  Evidence: `examples/node/wheelhouse-verification-matrix.yml` and negative
  schema tests. Only macOS arm64/Python 3.13 is currently candidate-passed.
- [x] Add hosted Linux, macOS and Windows/Python 3.13 jobs that stage every
  hash-pinned production wheel, disable package indexes for installation, run
  the installed synthetic node from a clean unrelated directory and retain a
  platform-specific receipt. Hosted success remains candidate evidence rather
  than custodian or independent-operator approval.

## Review fixes — hosted portability

- [x] Make the offline-install command-construction test recognize both
  `python` and `python.exe`, after the first hosted Windows run exposed the
  POSIX-only mock assumption. Runtime behavior was not reached by that failed
  job; exact-head hosted rerun evidence is required.
- [x] Add a repository-wide LF checkout policy for packaged text after hosted
  macOS and Windows receipts exposed different pure-wheel digests despite an
  identical installed synthetic result. Binary release formats are explicitly
  excluded; exact-head Windows/macOS digest comparison remains required.
- [x] Retain the platform-built node wheel with each hosted offline-install
  receipt so cross-platform byte drift can be diagnosed member-by-member rather
  than waived. Artifact retention is short-lived candidate evidence only.
- [x] Canonicalize generated wheel metadata, member order, ZIP attributes and
  `RECORD` after the backend build. Member comparison showed that Windows CRLF
  in `METADATA` was the sole content difference from macOS; a regression test
  now requires platform-different fixtures to become byte-identical.
- [x] Test incompatible versions, failed runs, correction and withdrawal. Evidence: strict semantic-version, terminal-status and immutable superseding-manifest tests.

## Phase 4 — External pilot readiness

- [x] Write draft operator, data-steward and export-review guidance. Evidence: `docs/federated-node-004-operator-guide.md` and threat model; approval remains open.
- [x] Complete repeatable two-invocation synthetic-node execution. Evidence: `docs/federated-node-004-independent-synthetic-run.md` and `make node-reproducibility`.
- [ ] Complete second-operator installation and synthetic-node execution on a supported environment.
- [x] Prepare non-binding controlled-environment pilot protocol and application pack. Evidence: `docs/federated-node-004-pilot-application-draft.md`; approval and activation remain external-gated.
- [x] Retain the controlled-pilot gate and define the bounded-scope reconsideration checkpoint. Evidence: `docs/decisions/ADR-0003-retain-controlled-pilot-gate.md`.
- [ ] Complete a pilot before v1 or remove controlled-pilot claims from scope.

## Phase 5 — Review

- [ ] Conduct scientific, privacy, security and engineering review.
- [x] Record residual risks and required local controls. Evidence: `docs/federated-node-004-threat-model.md`; external review remains open.
- [ ] Release the node alpha only after all blocking findings close.

## Review fixes — 2026-07-31

- [x] Add missing node input/output schemas and validate all four node fixtures.
- [x] Enforce aggregate dimension allowlists, nested-value rejection and case-normalised sensitive-field rejection.
- [x] Add local monotonic comparison primitives preventing analysis overrides from weakening a supplied custodian baseline; trusted policy loading remains open.
- [x] Add strict semantic-version parsing, canonical output fingerprints and correction lifecycle invariants.
- [x] Harden recursive log redaction for credential key variants and bearer/authorization values.
- [x] Correct independent-execution, packaging, signing and historical-review claims.
- [x] Add an explicitly synthetic common-analysis runner that rejects identifiers and overlapping-diagnosis double counting.
- [x] Add a deterministic, integrity-checked offline wheel-bundle builder for locally supplied artifacts; complete approved dependency staging remains open.
- [x] Add immutable disclosure-policy and query-ledger primitives without claiming custodian authority or durable persistence.

## Dependency review — 2026-07-27

- [x] Record that Track 004 cannot activate until Tracks 009 and 010 are complete. Evidence: `f919b03`.
