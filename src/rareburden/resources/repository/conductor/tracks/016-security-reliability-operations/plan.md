# Track 016 plan

## Phase 1 — Threat model and support scope

- [ ] Threat-model repository, acquisition, build, node, API and release boundaries.
- [ ] Declare supported runtimes and environments.
- [ ] Define security, incident, backup and recovery ownership.
- [ ] Define performance and availability budgets without unsupported service promises.

## Phase 2 — Supply-chain hardening

- [ ] Lock release dependencies and test reproducible builds.
- [ ] Add secret, dependency, licence and static security scanning.
- [ ] Generate SBOM, checksums and build provenance.
- [ ] Add release signing or verifiable attestation.

## Phase 3 — Operational controls

- [ ] Implement privacy-safe logging and metrics.
- [ ] Implement backup, restore, rollback and correction runbooks.
- [ ] Add benchmark and resource-regression tests.
- [ ] Verify source archives and Git clones with the same public command.

## Phase 4 — Exercises and release candidate

- [ ] Run vulnerability disclosure and incident tabletop exercise.
- [ ] Run backup/restore and release rollback exercises.
- [ ] Triage all security and reliability findings.
- [ ] Publish support and security-fix policy with primary and backup owners.
