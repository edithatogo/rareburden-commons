# Security and sensitive-data reporting

## Scope

The public repository should contain code, documentation, metadata, schemas, synthetic examples and approved aggregate outputs only.

## Reporting

Do not open a public issue containing credentials, participant information, small cells, security exploit details or controlled-data excerpts. Once the repository is hosted, use the hosting platform's private vulnerability-reporting channel or contact the designated institutional security lead. Until a host is appointed, remove the material from any branch under your control and notify the founding maintainer through an established private channel.

## Accidental sensitive-data commit

1. Stop sharing or pushing the branch.
2. Preserve only the minimum incident metadata needed for investigation.
3. Notify the data custodian and institutional privacy/security contacts where applicable.
4. Remove the material from Git history; deleting the latest file alone is insufficient.
5. Rotate any exposed credentials.
6. Document remediation and assess downstream clones, caches and releases.

## Supported versions

The project is pre-release. Security and privacy fixes apply to the current `main` branch until a formal support policy is adopted.
