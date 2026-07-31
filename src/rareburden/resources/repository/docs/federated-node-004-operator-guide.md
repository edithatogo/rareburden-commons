# Track 004 offline operator guide (draft)

This guide is preparatory and applies only to synthetic/offline execution.

1. Pin the repository revision and lockfile fingerprint.
2. Build and inspect the wheel with `uv run make build package-check`.
3. Install the wheel into a clean approved environment using the custodian's
   approved, pre-staged dependency source. The repository does not yet claim a
   complete offline dependency wheelhouse.
4. Run `uv run make installed-package-check`; this imports the installed
   `rareburden.node`, executes the synthetic aggregate fixture, and verifies its
   output fingerprint from an unrelated working directory.
5. Run `uv run make node-reproducibility` to verify deterministic
   packaging/runtime behavior in the checkout.
6. Run the local synthetic cohort through `run_offline_node`.
7. Inspect suppression statuses and confirm no participant fields are present.
8. Retain the execution manifest and environment identity with the review packet.
9. For an error, create a superseding manifest with `amend_execution_manifest`;
   never overwrite the original record.
10. For a withdrawal, mark the existing manifest withdrawn and stop distribution.

If installation needs network access, a schema check fails, a query-history receipt
is unavailable, or a fingerprint differs, stop without exporting and record the
failure for engineering and custodian review.

No operator may connect a node to a custodian, lower disclosure thresholds, or
publish an output without the applicable governance and export-review approvals.
