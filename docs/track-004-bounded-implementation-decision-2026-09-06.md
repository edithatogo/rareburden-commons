# Track 004 bounded implementation decision

Purpose: record the owner's bounded-implementation position for the federated
country-node execution package after the owner-operated clean-environment
rehearsal. Status: decided by repository owner (`edithatogo`, sole accountable
human) on 2026-09-06; bounded implementation position retained and the track
remains Blocked on external gates.
Starting repository commit: `283597c6ca6dcc8e78a74e41b04843490396635d`.

## What this decision accepts

The [owner-operated rehearsal receipt](track-004-owner-operated-rehearsal-2026-09-05.json)
is accepted as bounded synthetic evidence: a clean detached-worktree build of
the exact candidate (`a4d811544fe10276647527f45da6e9458986d15c`, tree
`8f8a1cc3a03f23b5359bb561dae6fc8aaf5dde8e`), a seven-wheel hash-pinned
wheelhouse, and an offline installation from documentation with package
indexes disabled, recorded through `scripts/check_offline_node_install.py`
(exit status 0, one result row). The rehearsal is owner-operated engineering
evidence on one macOS arm64 environment and nothing more.

Implementation, documentation and synthetic-only verification work may
continue. `scripts/check_track004_owner_rehearsal.py`, wired as
`make track-004-owner-rehearsal-check`, enforces that the receipt keeps its
independent-operation, custodian-approval, production-signing and
release-authorization claims false, and that the plan item stays recorded.

## Remaining gates (external, fail-closed)

Marking the rehearsal plan item complete records the rehearsal evidence only;
it does not close the track. The authoritative gate list is the
[2026-09-06 implementation and archive audit](../conductor/tracks/004-federated-node-runner/audit-2026-09-06.md),
which supersedes earlier gate summaries. The remaining acceptance gates are:

1. Phase 1 rights/data-use and community/harm advisory review plus owner
   disposition for the full contract.
2. Production common-analysis contract approval and a complete locked
   dependency wheel set for the supported target environments.
3. Integration with an authoritative custodian-controlled durable
   policy/query store; the local synthetic SQLite reference is insufficient
   evidence.
4. Panel challenge and owner disposition for the accepted package, covering
   the procedures that the retained one-row installation rehearsal does not
   exercise.
5. Full methods, privacy, security and engineering review and owner
   disposition.
6. Node-alpha release after its blocking findings close.

The current bounded advisory model requires no independent operator and no
actual community participation, and none is claimed. Controlled-data
activation remains disabled; no participant or controlled data were used and
none are authorized by this decision.

## Non-claims

This decision does not claim independent operation, custodian approval,
production signing, release authorization or empirical validity. The rehearsal
result is synthetic and offline-only. Stop on any attempt to present the
rehearsal as production readiness, to activate controlled data, or to release
node-alpha while the gates above remain open. No dissenting human assessment
has been collected; no human consensus is claimed.