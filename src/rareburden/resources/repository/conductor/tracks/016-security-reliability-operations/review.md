# Track 016 dependency review — Security, reliability and operations

**Review date:** 2026-08-01  
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
PRs #23–#29 passed their applicable exact-head protected matrices; PR #28
integrated the release-candidate foundations into protected default branch
`main`, and PR #29 corrected the Scorecard permission boundary.

Release dependencies and exported requirements are locked; wheel/sdist and
reference outputs reproduce deterministically; CodeQL, dependency/licence
review, `pip-audit`, repository safety, GitHub secret scanning/push protection
and Scorecard workflows are configured. SBOM, checksums and GitHub OIDC keyless
attestation are implemented with offline bundles and a fail-closed verifier.
The fresh hash-pinned production/development dependency audit passed on merged
commit `c71756b` in hosted run
`https://github.com/edithatogo/rareburden-commons/actions/runs/30669395458`.
A second default-branch audit passed on integrated commit `e017cdc` in hosted
run `https://github.com/edithatogo/rareburden-commons/actions/runs/30670769183`.
The corrected OpenSSF Scorecard workflow then passed on default-branch commit
`a6f91b7` in hosted run
`https://github.com/edithatogo/rareburden-commons/actions/runs/30670930650`.
The run produced retained SARIF and published-results evidence with an initial
score of 6.4. Its low or unavailable checks accurately reflect repository age,
the solo-maintainer/no-review policy, absence of a canonical release, and
external badge/ownership evidence; they are not silently treated as complete.

## Preparation refresh — 2026-08-01

`docs/track-016-operations-review-packet.md` records the exact receipts and
accountable dispositions still required. Repository-owned attestations and
scans remain evidence of preparation, not independent security review,
operational acceptance or production authorization.

The canonical prerelease tag `v0.3.0-rc.2` executed the release workflow
successfully in hosted run
`https://github.com/edithatogo/rareburden-commons/actions/runs/30686643886`.
The published prerelease retains the wheel, sdist, CycloneDX SBOM, checksums,
OIDC provenance/SBOM attestations, trusted root, profile and offline verifier:
`https://github.com/edithatogo/rareburden-commons/releases/tag/v0.3.0-rc.2`.
This closes the repository-owned SBOM/checksum/provenance receipt gate for the
release candidate. It does not constitute independent security review or an
operational exercise: backup/restore, incident, rollback and vulnerability
tabletop evidence, ownership, and Track 004/014 activation remain open.

## Bounded reconciliation — 2026-08-16

**Disposition:** repository-owned exercises pass; Track remains Planned.

Track 015 merged at exact commit
`abcf10813d9ad1dd88d8fac402622f65077558d4` and tree
`ccc08ef01f5eb0fc973fac3541a0a5f4976f4944`. The owner-operated clean-clone,
offline locked-environment, repository-safety, synthetic-node, SBOM,
backup/restore, rollback, resource-budget and synthetic incident-tabletop
exercises passed against that candidate. The redacted receipt is
`docs/track-016-owner-operated-exercise-receipt-2026-08-16.json`; the
machine-checked boundary is
`manifests/operations/track-016-bounded-operations-2026-08-16.json`.

Negative tests reject commit/tree or evidence-hash drift, unsafe paths,
authority/independence upgrades, a completed-backup claim, missing gates and an
overstated operator model. The bounded retention/access policy is operative for
repository-owned synthetic/public records only.

The evidence is owner-operated and therefore does not satisfy independent
operator or independent-security gates. The private backup owner is
owner-attested, but the scoped, expiring, hash-bound handoff remains incomplete.
Production operations, controlled data, SLA, stable release and release
authority remain pending and fail closed.
