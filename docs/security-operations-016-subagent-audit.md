# Track 016 security and operations subagent audit

**Status:** preparatory, repository-owned evidence only  
**Version:** 2026-08-01  
**Scope:** public repository, synthetic fixtures and offline release tooling

This packet records what an automated or delegated technical reviewer can
verify without access to a custodian environment. It is not a security
assurance, service-level commitment, production incident exercise or approval
to process controlled data.

## Audit lanes

| Lane | Repository-owned evidence | Result | Still required |
|---|---|---|---|
| Secrets and logs | Redaction tests in `tests/test_node.py` and acquisition/security tests; repository safety scanner; credential-free URL checks | Pass for synthetic fixtures | Independent review of deployed logging and host configuration |
| Supply chain | Locked `uv.lock`, deterministic CycloneDX builder, dependency/workflow checks, package inspection and release-attestation verifier | Pass for local candidate | Hosted CI results and release-owner disposition of advisories |
| Release integrity | Checksums, runtime-asset manifest, provenance profile and fail-closed attestation verification | Pass for offline tooling | Verified attestation receipt for an authorised release |
| Backup and rollback | `docs/synthetic-operations-016-exercise-protocol.md`, correction/withdrawal fixtures and isolated synthetic rehearsal | Pass for synthetic rehearsal | Custodian backup/restore, rollback and recovery-time evidence |
| Incident response | `docs/decisions/ADR-0004-keyless-release-attestation.md` and operations reference define containment, evidence preservation and closure | Draft contract | Named primary/backup owners and a completed tabletop |

## Reviewer procedure

An independent technical subagent may reproduce the local result by running
`uv run make check`, `uv run make reproducibility` and (where the build
environment permits) `uv run make release-check`. The reviewer must record the
commit, environment, commands, hashes, failures and disposition. A subagent
may recommend `pass`, `revise`, `bounded` or `stop`; it cannot approve a
production release or substitute for a custodian, security officer or release
authority.

## Fail-closed contingencies

- If hosted dependency, CodeQL, secret-scanning or attestation evidence is
  unavailable, keep the candidate offline and do not tag or publish it.
- If a restore or rollback rehearsal differs by hash, stop and issue a new
  candidate; do not waive drift as equivalent.
- If no accountable primary and backup operators are appointed, retain the
  public/synthetic scope and make no uptime or support claim.
- If a deployed log or configuration review finds sensitive output, withdraw
  the affected artefact, preserve the incident receipt and require remediation
  before any release decision.

## Decision boundary

This audit closes repository-owned preparation only. It deliberately leaves
security acceptance, operational ownership, custodian controls, controlled-data
access and release authority open until the required accountable receipts are
available.
