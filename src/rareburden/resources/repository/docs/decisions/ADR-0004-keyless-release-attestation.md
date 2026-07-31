# ADR-0004 — GitHub OIDC keyless release attestation

**Status:** accepted for repository release engineering on 31 July 2026;
custodian acceptance and controlled-node activation remain pending.

## Decision

RareBurden Commons release artifacts use GitHub-hosted, OIDC-backed keyless
Sigstore attestations generated only by `.github/workflows/release.yml` for
canonical `v*` tags. No long-lived maintainer signing key is created.

The release workflow:

1. builds and checks the tagged source with locked dependencies;
2. generates checksums and a CycloneDX SBOM;
3. attests the distributions, SBOM and checksum manifest using the pinned
   `actions/attest` revision;
4. retains the provenance and SBOM Sigstore bundles, a per-release trusted-root
   snapshot, the verification profile and their checksums with the release; and
5. publishes only after all prior steps pass.

Offline verification must enforce every constraint in
`examples/config/release-attestation-profile.json`: exact repository, exact
signer workflow, GitHub Actions OIDC issuer, SLSA provenance predicate, canonical
tag source ref and denial of self-hosted runners. The repository wrapper delegates
cryptographic verification to GitHub CLI and fails closed.

## Rationale

This profile removes long-lived private-key custody from a single-maintainer
repository while binding provenance to the protected release workflow. Retained
Sigstore bundles and trusted-root snapshots support disconnected verification.
GitHub recommends refreshing trusted roots whenever new signed material enters an
offline environment because later revocations cannot be learned while offline.

The command and bundle behavior follow the official
[GitHub offline-verification guidance](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline),
[GitHub CLI verification contract](https://cli.github.com/manual/gh_attestation_verify)
and [`actions/attest` bundle output](https://github.com/actions/attest).

## Security boundary

- A checksum without a successfully verified attestation does not authenticate a
  release.
- Predicate content alone is not treated as an unforgeable identity claim.
  Verification relies on the certificate identity and witnessed timestamps.
- The release environment, tag protection and GitHub account security remain
  part of the trust boundary.
- A stale trusted-root snapshot may not reveal a later revocation. Operators must
  refresh it per release on an approved online transfer host.
- Repository implementation does not constitute custodian acceptance, security
  accreditation, independent operation or authorization to process controlled
  data.

## Rollback and incident response

On suspected workflow, account or release compromise:

1. disable the release environment and stop distribution;
2. mark the affected release withdrawn and preserve evidence;
3. rotate compromised GitHub credentials and review workflow/tag changes;
4. obtain fresh trusted roots on an approved host;
5. rebuild from a reviewed clean tag and issue a superseding release; and
6. require custodians to reject the affected artifact digest.

The repository must not silently replace an immutable released artifact.
