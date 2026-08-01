# Track 016 backup, restore, rollback and incident runbook draft

**Status:** non-production template for synthetic/offline rehearsals.

## Backup and restore

1. Freeze the release identifier and record the manifest and SHA-256 checksums.
2. Copy only the public release bundle, synthetic fixtures and value-free
   receipts to an isolated destination.
3. Verify the destination against the manifest before opening any artefact.
4. Restore into a clean environment and run `uv run make check` plus the
   release-attestation verifier.
5. Compare generated outputs and receipts with the recorded hashes.
6. Record operator, platform, Python version, commands, failures and disposition.

## Rollback and correction

Rollback selects a previously verified immutable release; it never rewrites a
receipt or silently substitutes a missing input. Corrections and withdrawals
must create a new version with a supersession link and preserve the prior
manifest for audit.

## Incident response

Contain the affected release or node, preserve value-free logs and manifests,
revoke exposed credentials, assess disclosure and governance impact, notify the
accepted security contact, and record corrective action. Do not copy controlled
or participant-level data into an incident ticket or public issue.

## Exercise boundary

This template supports a synthetic rehearsal only. A production exercise still
requires named primary and backup operators, an independent witness, custodian
approval, retention authority and a signed receipt. Until those exist, Track
016 remains blocked and no operational support promise is made.
