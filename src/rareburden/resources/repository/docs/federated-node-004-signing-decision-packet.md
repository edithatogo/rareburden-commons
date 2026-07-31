# Track 004 signing and attestation decision packet

**Status:** non-binding; no trust root, key custodian or production signing
method is approved by this document.

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

## Recommendation

Approve option C only if participating custodians can operate and audit both
trust paths. Otherwise approve option A for the first controlled pilot, with
two-person release authorization, hardware-backed key storage, an offline
revocation list, a tested rotation ceremony and a later migration path to
transparency-backed provenance. Do not implement cryptographic signing until
the authority, key custody and verification-failure policy are named.

## Evidence required to close the gate

- signed architecture decision identifying the option and accountable roles;
- key-generation/custody/backup/rotation/revocation ceremony record;
- canonical signed-payload specification and test vectors;
- positive, tamper, expired/revoked-key and wrong-trust-root verification tests;
- an independently operated offline installation receipt;
- custodian acceptance of verification tooling and failure behavior; and
- incident-response exercise covering compromised release credentials.

Existing SHA-256 bundle and wheel checks protect integrity after a trusted
manifest is obtained. They do not authenticate the manifest or establish a
release authority.
