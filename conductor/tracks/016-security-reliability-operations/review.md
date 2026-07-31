# Track 016 dependency review — Security, reliability and operations

**Review date:** 2026-07-29  
**Decision:** Planned; hardening not activated

## Findings

- Tracks 004 and 014 are incomplete, so node/API production pathways are not
  available for operational assurance.
- Local repository safety, dependency lock, SBOM, checksum and provenance checks
  exist, but they do not constitute independent security review or an operational
  exercise.
- Security, data-governance, engineering and release gates remain required.

## Local preparation

`docs/security-operations-016-reference.md` records boundary threats, fail-closed
controls, logging/data invariants and release-readiness gates without making
service-level promises.

## Activation gates

- Supported-runtime and performance budget decision.
- Independent threat/security review and vulnerability-disclosure exercise.
- Backup/restore/rollback evidence with named primary and backup owners.
- Track 004/014 completion and release authority approval.

## Repository evidence refresh — 2026-08-01

The repository now declares a bounded supported-environment matrix: Linux runs
the full Python 3.11–3.14 compatibility checks, while Python 3.13 carries the
complete release assurance and Linux/macOS/Windows offline-install evidence.
PRs #23–#25 passed their exact-head protected matrices.

Release dependencies and exported requirements are locked; wheel/sdist and
reference outputs reproduce deterministically; CodeQL, dependency/licence
review, `pip-audit`, repository safety, GitHub secret scanning/push protection
and Scorecard workflows are configured. SBOM, checksums and GitHub OIDC keyless
attestation are implemented with offline bundles and a fail-closed verifier.
The fresh hash-pinned production/development dependency audit passed on merged
commit `c71756b` in hosted run
`https://github.com/edithatogo/rareburden-commons/actions/runs/30669395458`.
The Scorecard workflow is present on the handoff branch but cannot be manually
dispatched until it is also present on the repository's default branch; this is
a default-branch integration gap, not completed Scorecard evidence.

No canonical tag has executed the release workflow, so build provenance and
verifiable-attestation tasks remain pending despite their implementation. The
same distinction applies to operational controls: configuration and synthetic
tests are not backup/restore, incident, rollback or vulnerability table-top
exercises. Track 016 remains planned and dependency-blocked.
