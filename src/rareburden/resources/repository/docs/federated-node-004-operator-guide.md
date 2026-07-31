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
4. Before installation, verify the release provenance using the artifact,
   `verify_release_attestation.py`, `provenance.sigstore.json`,
   `trusted_root.jsonl` and `profile.json` retained with the same GitHub
   release. In a checkout, use:

   ```sh
   uv run make release-attestation-verify \
     ARTIFACT=/approved/wheelhouse/rareburden-<version>-py3-none-any.whl \
     ATTESTATION_BUNDLE=/approved/evidence/provenance.sigstore.json \
     TRUSTED_ROOT=/approved/evidence/trusted_root.jsonl \
     SOURCE_REF=refs/tags/v<version> \
     RECEIPT=/approved/evidence/verification-receipt.json
   ```

   This invokes GitHub CLI offline and enforces the repository profile. Stop on
   any digest, certificate, issuer, repository, workflow, predicate, source-ref,
   runner or trusted-root failure. A custodian must approve how trusted roots
   are refreshed and transferred before controlled use.

   Outside a checkout, run the retained script directly and supply
   `--profile /approved/evidence/profile.json` plus the same artifact, bundle,
   trusted-root and source-ref arguments.
5. Install the verified wheels into a clean approved environment using only the
   custodian's approved local source.
   The repository rehearsal can be repeated with:

   ```sh
   uv run make offline-node-install \
     NODE_WHEEL=/approved/wheelhouse/rareburden-<version>-py3-none-any.whl \
     WHEELHOUSE=/approved/wheelhouse \
     PYTHON_VERSION=3.13
   ```
6. Run `uv run make installed-package-check`; this imports the installed
   `rareburden.node`, executes the synthetic aggregate fixture, and verifies its
   analysis, policy-ledger and output fingerprint from an unrelated working
   directory.
7. Run `uv run make node-reproducibility` to verify deterministic
   packaging/runtime behavior in the checkout.
8. Run an explicitly synthetic cohort through
   `aggregate_synthetic_records`, register its value-free query shape in a
   `QueryLedger` snapshot, then pass the resulting aggregate rows to
   `run_offline_node`.
9. Inspect suppression statuses and confirm no participant fields are present.
10. Retain the verification receipt, execution manifest and environment identity
    with the review packet.
11. For an error, create a superseding manifest with `amend_execution_manifest`;
   never overwrite the original record.
12. For a withdrawal, mark the existing manifest withdrawn and stop distribution.

If installation needs network access, a schema check fails, a query-history receipt
is unavailable, or a fingerprint differs, stop without exporting and record the
failure for engineering and custodian review.

No operator may connect a node to a custodian, lower disclosure thresholds, or
publish an output without the applicable governance and export-review approvals.
The in-memory policy and ledger snapshots are reference primitives, not a
custodian-controlled durable system of record.
