# Track 004 dependency review — Federated country-node execution package

**Review date:** 2026-07-27  
**Decision:** Blocked pending Tracks 009 and 010

## Findings

- Track 006 is complete, but Track 009 remains planned and Track 010 depends on Track 009.
- The node contracts, disclosure policy, version negotiation and synthetic runner are not yet implemented in Track 004.
- Data-governance, patient/community, engineering and security gates remain required before any controlled-node pilot claim.

Repository-owned progress now includes an offline aggregate-export primitive
that rejects participant-level fields and suppresses small cells, with focused
negative tests. It does not connect to custodians or establish a pilot contract.

### Review rerun — 2026-07-29

Repository review result: **Pass with dependency and governance gates**. The
disclosure boundary and tests are deterministic, and the full validation gate
passes. Track 004 remains blocked pending Tracks 009/010 and data-governance,
patient/community, engineering and security review.

### Blocker resolution matrix — 2026-07-29

| Blocker | Local resolution | Remaining gate |
|---|---|---|
| Unspecified node/disclosure contracts | Added execution-manifest and disclosure-policy schemas plus synthetic fixtures | Data-governance and engineering approval |
| Participant-level export risk | Export validator rejects participant fields and suppresses small cells | Custodian-specific thresholds and privacy review |
| Controlled execution authorization | No custodian connection or person-level execution added | Approved node pilot and patient/community review |
| Signing/attestation | Manifest supports input/output fingerprints; signing remains unclaimed | Release/security authority |

The manifest builder now validates non-empty identifiers, bounds status values
and rejects incompatible major versions. It remains a deterministic offline
preflight helper; it does not attest an environment or authorize execution.

The preflight also captures only bounded runtime identity and a caller-supplied
lockfile fingerprint. It excludes credentials, host paths, and participant data;
environment attestation and controlled execution remain gated.

The synthetic `run_offline_node` helper now composes manifest creation with the
disclosure validator. It is deterministic and memory-only, with negative coverage
for participant-level rows; it is not a portable package or controlled pilot.

## Disposition

Keep Track 004 **blocked**. Do not activate federated execution or controlled-environment pilot work until the evidence/parameter ledger and burden-engine dependencies are complete.
