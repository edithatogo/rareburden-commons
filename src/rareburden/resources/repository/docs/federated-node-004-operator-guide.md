# Track 004 offline operator guide (draft)

This guide is preparatory and applies only to synthetic/offline execution.

1. Pin the repository revision and lockfile fingerprint.
2. Run the local synthetic cohort through `run_offline_node`.
3. Inspect suppression statuses and confirm no participant fields are present.
4. Retain the execution manifest and environment identity with the review packet.
5. For an error, create a superseding manifest with `amend_execution_manifest`;
   never overwrite the original record.
6. For a withdrawal, mark the existing manifest withdrawn and stop distribution.

No operator may connect a node to a custodian, lower disclosure thresholds, or
publish an output without the applicable governance and export-review approvals.
