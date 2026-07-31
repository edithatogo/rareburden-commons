# Track 004 offline operator guide (draft)

This guide is preparatory and applies only to synthetic/offline execution.

1. Pin the repository revision and lockfile fingerprint.
2. Run `uv run make node-reproducibility` to verify deterministic packaging/runtime behavior.
3. Run the local synthetic cohort through `run_offline_node`.
4. Inspect suppression statuses and confirm no participant fields are present.
5. Retain the execution manifest and environment identity with the review packet.
6. For an error, create a superseding manifest with `amend_execution_manifest`;
   never overwrite the original record.
7. For a withdrawal, mark the existing manifest withdrawn and stop distribution.

No operator may connect a node to a custodian, lower disclosure thresholds, or
publish an output without the applicable governance and export-review approvals.
