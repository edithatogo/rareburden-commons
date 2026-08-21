# Security and sensitive-data reporting

The detailed owner-operated support and security-fix policy is
[`docs/track-016-support-security-fix-policy.md`](docs/track-016-support-security-fix-policy.md).
It is a pre-release policy without a response-time or service-level promise.

## Scope

The public repository contains code, documentation, metadata, schemas,
synthetic examples and approved aggregate outputs only. The project is
pre-release. Security and privacy fixes are applied to the current `main`
branch as owner capacity permits; prerelease tags and historical branches do
not receive continuing fixes.

## Reporting

Do not open a public issue containing credentials, participant information,
small cells, exploit details or controlled-data excerpts. Use the repository's
[private vulnerability-reporting channel](https://github.com/edithatogo/rareburden-commons/security/advisories/new).
If that external channel is unavailable, remove the material from branches
under your control and notify repository owner `edithatogo` through an
established private channel. Do not create a public fallback disclosure that
contains sensitive material.

## Accidental sensitive-data commit

1. Stop sharing or pushing the branch.
2. Preserve only the minimum incident metadata required for investigation.
3. Notify the custodian and institutional privacy/security contacts where applicable.
4. Remove the material from Git history; deleting only the latest file is insufficient.
5. Rotate exposed credentials.
6. Assess downstream clones, caches, releases and logs.
7. Document remediation, correction or withdrawal.

## Stable-v1 security target

Before v1.0, the project must have a tested threat model, locked release
dependencies, secret/dependency/licence scanning, SBOM, build provenance,
signed or attested artefacts, incident response, backup/recovery and rollback.
`edithatogo` is the sole accountable security owner. Recovery procedures and
encrypted recovery material may reduce continuity risk but do not create a
backup owner or co-maintainer. Owner unavailability or suspected credential
compromise freezes protected changes, production operations and releases. The
blocking criteria are in `docs/v1-acceptance-criteria.md`.
