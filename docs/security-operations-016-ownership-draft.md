# Track 016 security and operations ownership draft

**Status:** non-binding preparation; no role has been accepted.

This draft makes the decisions needed for operational readiness explicit. It is
not an appointment, service-level commitment, or authorization to process
controlled data.

## Roles requiring named acceptance

| Role | Primary | Backup | Evidence required |
|---|---|---|---|
| Security contact | pending | pending | written acceptance and contact route |
| Incident coordinator | pending | pending | tabletop participation and escalation authority |
| Release operator | pending | pending | release-candidate rehearsal and signing authority |
| Backup/restore operator | pending | pending | successful restore and rollback receipt |
| Data-governance liaison | pending | pending | custodian/community decision record |

Until every primary and backup is accepted, the repository remains a public
reference implementation only. No uptime, response-time, on-call, or support
promise may be inferred.

## Minimum handoff packet

An accepted handoff must identify the release commit/tag, supported runtime,
authorised artefact locations, escalation window, evidence-retention period,
correction/withdrawal authority, and a successor or expiry date. Secrets and
participant-level data must never be included in the packet.

## Contingency

If no staffed operational owner is available, retain the synthetic/offline scope,
publish the runbooks as preparation only, and do not activate production node or
API pathways. A time-limited interim owner may be proposed, but requires written
acceptance and an explicit expiry before it can close this gate.
