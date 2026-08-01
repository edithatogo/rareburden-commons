# Track 016 plan

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

- [ ] Implement privacy-safe logging and metrics.
- [ ] Implement backup, restore, rollback and correction runbooks.
- [ ] Add benchmark and resource-regression tests.
- [x] Add a bounded runtime regression gate for the synthetic reference burden
  workload. Evidence: `scripts/check_burden_benchmark.py` runs in `make check`;
  memory, package-size and representative large-workload budgets remain open.
- [ ] Verify source archives and Git clones with the same public command.

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
