# Track 004 signing and attestation decision packet

**Status:** decision recorded. ADR-0004 approves option B for repository release
engineering. Custodian acceptance, controlled-node activation and an independent
offline verification receipt remain external gates.

## Decision required

The release/security authority and participating custodians must approve:

1. the artifact identity that is signed (bundle manifest digest, wheel digests,
   node version and policy/profile identifier);
2. the trust model (offline organisational key, keyless transparency service,
   or a documented hybrid);
3. key ownership, quorum, storage, rotation, revocation and incident response;
4. verification software and the trusted root material installed at each node;
5. whether verification is mandatory before installation and execution;
6. the retention period for signatures, certificates, transparency receipts
   and verification logs; and
7. the migration and emergency rollback process.

## Options

### A — Offline organisational signing

An authorised release role signs the canonical bundle-manifest digest using a
key protected by approved organisational key management. Nodes verify against
pre-distributed trust roots. This supports disconnected installation but creates
key-custody, rotation and revocation responsibilities.

### B — Keyless transparency-backed signing

An approved workload or maintainer identity obtains a short-lived certificate
and records the signing event in a transparency service. This improves identity
and audit evidence, but signing and initial receipt acquisition require an
available external service; offline nodes still need a complete verification
bundle and trusted roots.

### C — Hybrid

Release artifacts carry both an offline organisational signature and
transparency-backed provenance. This offers the strongest independent evidence
but has the highest operational and recovery complexity.

## Decision

Use option B: GitHub OIDC keyless Sigstore attestations from the pinned release
workflow, with release-retained bundles, a per-release trusted-root snapshot and
an identity-constrained offline verifier. This avoids an unstaffed long-lived key
custody ceremony in the single-maintainer repository. See
`docs/decisions/ADR-0004-keyless-release-attestation.md`.

Custodians must still approve their trusted-root transfer, retention,
verification-failure and incident-response procedures before controlled-node
activation. A later hybrid profile requires a new decision and staffed key
custody; it is not implied by this decision.

## Evidence required to close the gate

- custodian acceptance of ADR-0004 and accountable local roles;
- canonical subject/profile evidence and positive, tamper, stale/revoked-root,
  wrong-identity and wrong-ref verification evidence;
- an independently operated offline installation receipt;
- custodian acceptance of verification tooling and failure behavior; and
- incident-response exercise covering compromised release credentials.

Repository tests cover fail-closed profile and command behavior; only a real
tagged release can supply cryptographic positive evidence. Existing SHA-256
bundle and wheel checks protect integrity after a trusted manifest is obtained;
they do not independently authenticate the manifest.
