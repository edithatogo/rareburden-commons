# Track 016 synthetic operations exercise protocol

**Status:** Non-production reference exercise  
**Scope:** Public repository and synthetic/offline artefacts only

This protocol validates the repository-owned shape of operational controls. It
does not test a custodian service, controlled data, production availability,
or an accountable backup owner.

## Exercise sequence

1. Build a clean release bundle and record its commit, tag, checksums, SBOM and
   attestation evidence.
2. Copy the public release manifest, synthetic policy store database and
   value-free receipts into an isolated temporary workspace.
3. Restore the copy into a fresh environment and run the offline validation,
   schema checks, receipt-chain verification and synthetic node reproduction.
4. Inject a changed receipt, missing artefact and mismatched checksum; confirm
   that each validation fails closed.
5. Apply a correction/withdrawal fixture and verify that supersession is
   represented without rewriting the prior receipt.
6. Roll back to the previous synthetic release and record the resulting
   release, tool and fixture identities.

## Required receipt

Record the exact commit/tag, command transcript, platform/Python version,
input/output hashes, failure cases, operator identity and unresolved findings.
Store the receipt beside the release evidence; never include credentials,
participant records or controlled data.

## Boundary

A passing exercise is repository-owned synthetic evidence. It does not satisfy
the stable-v1 requirement for a production backup/restore exercise, named
primary and backup owners, an independent operator, or a controlled pilot.
