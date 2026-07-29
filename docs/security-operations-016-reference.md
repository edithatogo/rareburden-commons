# Track 016 security and operations reference

This is a preparatory control scaffold, not an independent security assurance or
service-level commitment.

## Boundary threats and controls

| Boundary | Primary threats | Required control |
|---|---|---|
| Repository | secret leakage, unsafe workflow changes, dependency drift | repository safety scan, locked dependencies, review and branch protection |
| Acquisition | SSRF, redirects, oversized/malformed bytes, terms violation | opt-in HTTPS, bounded hosts/addresses/size/timeouts, checksum and fail-closed terms |
| Build/release | tampered artefacts, non-reproducible outputs, provenance gaps | SBOM, checksums, release manifest, clean clone/archive verification |
| Node/custodian | privilege misuse, disclosure, local policy conflict | least privilege, local governance authority, aggregate-only export, custodian controls |
| API/product | injection, sensitive output, stale/corrected data | schema validation, redaction, immutable versioned releases, correction/withdrawal metadata |
| Operations | missed incidents, failed restore, unclear ownership | runbooks, primary/backup owners, tabletop and restore exercises |

Automated checks are evidence, not a substitute for independent security review,
custodian controls or staffed operational capacity.

## Operational invariants

- Credentials and tokens never enter logs, manifests, fixtures or public commits.
- Participant-level and controlled data remain inside the authorised node.
- Missing, withdrawn or superseded inputs cannot silently become zero or current.
- No uptime, response-time or support promise is made until capacity and owners
  are approved.
- Every incident records scope, containment, evidence preservation, correction and
  closure authority.

## Release readiness gates

Security review, SBOM/checksum/provenance evidence, benchmark results,
backup/restore and rollback exercises, vulnerability-disclosure tabletop, and
named primary/backup owners are required before production hardening is complete.
