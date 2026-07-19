# Security and sensitive-data reporting

## Scope

The public repository contains code, documentation, metadata, schemas, synthetic examples and approved aggregate outputs only. The current project is pre-release; security and privacy fixes apply to the current maintained branch until the stable support policy in Track 016 is approved.

## Reporting

Do not open a public issue containing credentials, participant information, small cells, exploit details or controlled-data excerpts. Once hosted, use the platform's private vulnerability-reporting channel or the designated institutional security contact. Until a host is appointed, remove the material from branches under your control and notify the founding maintainer through an established private channel.

## Accidental sensitive-data commit

1. Stop sharing or pushing the branch.
2. Preserve only the minimum incident metadata required for investigation.
3. Notify the custodian and institutional privacy/security contacts where applicable.
4. Remove the material from Git history; deleting only the latest file is insufficient.
5. Rotate exposed credentials.
6. Assess downstream clones, caches, releases and logs.
7. Document remediation, correction or withdrawal.

## Stable-v1 security target

Before v1.0, the project must have a tested threat model, locked release dependencies, secret/dependency/licence scanning, SBOM, build provenance, signed or attested artefacts, incident response, backup/recovery, rollback and named primary and backup security owners. The blocking criteria are in `docs/v1-acceptance-criteria.md`.
