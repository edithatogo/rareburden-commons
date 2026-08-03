# Track 016 plan

> Repository-owned review uses the subagent panel under ADR-0008; independent security and named operational-owner acceptance remain separate.

## Phase 1 — Threat model and support scope

- [x] Threat-model repository, acquisition, build, node, API and release boundaries. Evidence: `docs/security-operations-016-reference.md`; independent review remains open.
- [x] Declare supported runtimes and environments. Evidence:
  `docs/supported-environments.md` distinguishes continuously tested Linux
  Python 3.11–3.14 from Python 3.13 cross-platform candidate evidence and
  explicitly excludes unverified/custodian claims.
- [ ] Define security, incident, backup and recovery ownership.
- [x] Define performance/availability boundary without unsupported service promises. Evidence: reference scaffold explicitly withholds service-level commitments pending capacity/owner approval.

## Phase 2 — Supply-chain hardening

- [x] Lock release dependencies and test reproducible builds. Evidence:
  `uv.lock`, hash-pinned requirements exports, deterministic wheel/sdist
  builders, exact two-process reproduction, installed-package checks and the
  cross-platform exact-wheel evidence from PR #23.
- [x] Add secret, dependency, licence and static security scanning. Evidence:
  repository-safety checks, GitHub secret scanning/push protection, CodeQL,
  dependency review with licence policy, scheduled hash-pinned `pip-audit` and
  pinned OpenSSF Scorecard workflow. Automated scanning is not independent
  security review.
- [x] Generate SBOM, checksums and build provenance. Evidence: canonical
  prerelease run `30686643886` and retained release assets.
- [x] Add release signing or verifiable attestation. Evidence: OIDC-backed
  provenance/SBOM attestations, trusted root, profile and offline verifier in
  the canonical prerelease.
- [x] Configure fail-closed SBOM/checksum/provenance and keyless-attestation
  generation with retained offline verification evidence. Evidence: release
  workflow, ADR-0004, schema/profile/verifier, PR #24 and canonical run
  `30686643886`.

## Phase 3 — Operational controls

- [x] Implement privacy-safe log redaction. Evidence: recursive node-log and
  acquisition URL redaction with negative tests in `tests/test_node.py` and
  `tests/test_acquisition_security.py`; no participant or credential values are
  retained.
- [ ] Define and exercise privacy-safe operational metrics, retention and
  access controls.
- [x] Implement a metadata-only operational metric record primitive with
  sensitive-label rejection. Evidence: `rareburden.operations` and
  `tests/test_operations_metrics.py`; retention, access controls and production
  ownership remain open.
- [ ] Execute backup, restore and rollback runbooks against a clean locked
  environment.
- [x] Prepare repository-owned correction, withdrawal, backup and rollback
  runbook procedures. Evidence: `docs/synthetic-operations-016-exercise-protocol.md`,
  `docs/release-policy.md` and `docs/security-operations-016-reference.md`;
  production exercise and named-owner acceptance remain open.
- [x] Add deterministic benchmark tests. Evidence: `tests/test_burden_benchmark.py`
  covers reproducibility and fail-closed budget violations.
- [x] Add provisional package-size resource-regression policy and fail-closed
  checker. Evidence: `docs/track-016-package-size-policy.yml`,
  `scripts/check_package_size_policy.py` and `make package-size-check`.
  Installed-footprint and wheelhouse budgets remain separately measured.
- [x] Add a representative large-workload resource-regression test. Evidence:
  `tests/test_burden_benchmark.py` runs the 100,000-iteration synthetic
  workload under the bounded 15-second envelope; this remains synthetic
  evidence and makes no real-world capacity claim.
- [x] Add a bounded runtime regression gate for the synthetic reference burden
  workload. Evidence: `scripts/check_burden_benchmark.py` runs in `make check`;
  memory, package-size and representative large-workload budgets remain open.
- [x] Verify source archives and Git clones with the same public command.
  Evidence: clean-clone, wheel and source-archive validation recorded in
  `conductor/tracks/002-public-source-acquisition/review.md` (evidence `39a4b4d`).
  Cross-platform hosted reproduction remains open.

## Phase 4 — Exercises and release candidate

- [ ] Run vulnerability disclosure and incident tabletop exercise.
- [ ] Run backup/restore and release rollback exercises.
- [x] Prepare a bounded synthetic operations exercise protocol. Evidence:
  `docs/synthetic-operations-016-exercise-protocol.md`; execution and production
  ownership remain open.
- [ ] Triage all security and reliability findings.
- [ ] Publish support and security-fix policy with primary and backup owners.

## Preparatory dependency review — 2026-07-29

- [x] Document threat boundaries, operational invariants and activation gates
  without activating production hardening. Evidence: reference and review records.

## Preparation refresh — 2026-08-01

- [x] Prepared `docs/track-016-operations-review-packet.md` with exact
  security, runtime, recovery, privacy, supply-chain and owner evidence.
- [ ] Keep production pathways and support promises disabled until independent
  review and named-owner acceptance are recorded.

## Implementation planning — 2026-08-02

- [x] Add the dependency-ordered recovery, rollback, budget, retention/access
  and ownership plan with options, contingencies and recommendation in
  `docs/track-016-operations-implementation-plan-2026-08-02.md`.
- [x] Define and test the versioned resource-budget contract. Evidence:
  `rareburden.operations.build_resource_budget` and
  `tests/test_operations_budget.py` fail closed on invalid or over-budget
  measurements; production capacity claims remain disabled.
- [x] Draft the retention/access policy for operational records. Evidence:
  `docs/track-016-retention-access-policy.md`; it remains non-operative until
  security, data-governance and named-owner acceptance.
- [x] Add a metadata-only synthetic recovery/rollback receipt primitive with
  fail-closed identity and outcome checks in `rareburden.operations` and
  `tests/test_operations_budget.py`; production exercise evidence remains open.
- [x] Add a schema-validated synthetic operations receipt fixture and negative
  boundary test in `schemas/synthetic-operations-receipt.schema.json` and
  `tests/test_synthetic_operations_receipt.py`.
- [ ] Implement and execute clean-environment backup, restore and rollback
  exercises with redacted, hash-bound receipts.
- [ ] Record named primary/backup operational owners and escalation acceptance.
- [x] Record bounded repository-owner primary acceptance and explicit
  unassigned-backup contingency. Evidence:
  `docs/decisions/2026-08-03-owner-operated-operations-acceptance.md`; this
  does not close the qualifying operational-owner gate.
- [ ] Complete independent security/operator and release-authority gates before
  production-hardening activation.
- [x] Prepare the candidate-bound independent-operator and security evidence
  plan with panel and owner-operated boundaries. Evidence:
  `docs/track-016-independent-security-operator-plan-2026-08-03.md`; the
  qualifying independent receipts remain pending.

## Release disposition — 2026-08-03

- [x] Record a time-limited bounded owner disposition for the frozen
  synthetic/public candidate. Evidence:
  `docs/decisions/2026-08-03-owner-bounded-release-disposition.md`.
- [ ] Obtain a qualifying release-authority receipt before any stable-v1,
  hosted, controlled-data or production claim; the owner disposition is not an
  independent or external release approval.

## Clean-node rehearsal follow-up — 2026-08-03

- [x] Re-run the normative Python 3.13 offline-node rehearsal with the locked
  3.13 environment. Evidence: `dist/offline-install-receipt.json`; the
  hash-bound wheelhouse installed successfully with network disabled.
- [x] Run a supplemental network-disabled Python 3.14 rehearsal. Evidence:
  `dist/offline-install-receipt.json`; this is local compatibility evidence,
  not an independent operator receipt or release approval.
- [ ] Keep the release runtime at Python 3.13 unless a separately recorded
  compatibility decision changes the support matrix and refreshes the frozen
  candidate.
