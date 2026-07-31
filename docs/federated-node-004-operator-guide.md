# Track 004 offline operator guide (draft)

This guide is preparatory and applies only to synthetic/offline execution.

1. Pin the repository revision and lockfile fingerprint.
2. Build and inspect the wheel with `uv run make build package-check`.
3. Once every approved dependency wheel has been pre-staged locally, build a
   deterministic transport bundle:

   ```sh
   uv run python scripts/build_node_bundle.py build \
     --output dist/rareburden-node-bundle.zip \
     --node-wheel /approved/wheelhouse/rareburden-<version>-py3-none-any.whl \
     --dependency-wheel /approved/wheelhouse/dependency.whl
   uv run make node-bundle-check BUNDLE=dist/rareburden-node-bundle.zip
   ```

   Repeat `--dependency-wheel` for every locked dependency. The builder never
   downloads artifacts. The repository does not claim that a complete approved
   dependency wheel set has been staged.
4. Install the verified wheels into a clean approved environment using only the
   custodian's approved local source.
5. Run `uv run make installed-package-check`; this imports the installed
   `rareburden.node`, executes the synthetic aggregate fixture, and verifies its
   analysis, policy-ledger and output fingerprint from an unrelated working
   directory.
6. Run `uv run make node-reproducibility` to verify deterministic
   packaging/runtime behavior in the checkout.
7. Run an explicitly synthetic cohort through
   `aggregate_synthetic_records`, register its value-free query shape in a
   `QueryLedger` snapshot, then pass the resulting aggregate rows to
   `run_offline_node`.
8. Inspect suppression statuses and confirm no participant fields are present.
9. Retain the execution manifest and environment identity with the review packet.
10. For an error, create a superseding manifest with `amend_execution_manifest`;
   never overwrite the original record.
11. For a withdrawal, mark the existing manifest withdrawn and stop distribution.

If installation needs network access, a schema check fails, a query-history receipt
is unavailable, or a fingerprint differs, stop without exporting and record the
failure for engineering and custodian review.

No operator may connect a node to a custodian, lower disclosure thresholds, or
publish an output without the applicable governance and export-review approvals.
The in-memory policy and ledger snapshots are reference primitives, not a
custodian-controlled durable system of record.
