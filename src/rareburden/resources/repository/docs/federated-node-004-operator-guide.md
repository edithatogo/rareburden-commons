# Track 004 offline operator guide (draft)

This guide is preparatory and applies only to synthetic/offline execution. It
does not authorise a controlled-data connection, production node or export.

## Preparation and separate installation

1. Pin and record the repository commit/tree, lockfile and requirements hashes,
   operator role, OS/architecture, actual Python patch version and `uv` version.
   Use a clean checkout with an already provisioned development environment.
2. Build and inspect the wheel with `uv run make build package-check`.
3. Once every approved dependency wheel has been pre-staged locally, build a
   deterministic transport bundle:

   ```sh
   uv run python scripts/build_node_bundle.py build \
     --output dist/rareburden-node-bundle.zip \
     --node-wheel /approved/project/rareburden-<version>-py3-none-any.whl \
     --dependency-wheel /approved/wheelhouse/dependency.whl
   uv run make node-bundle-check BUNDLE=dist/rareburden-node-bundle.zip
   ```

   Repeat `--dependency-wheel` for every locked dependency. The builder never
   downloads artifacts. It verifies structure/hashes, not dependency closure or
   approval. Choose a new output path to preserve prior artifacts. Keep the
   project wheel outside the dependency-only wheelhouse: the install script
   rejects the project wheel appearing there, non-wheel files and symlinks.
4. For a tagged release, verify the release provenance using the artifact,
   `verify_release_attestation.py`, `provenance.sigstore.json`,
   `trusted_root.jsonl` and `profile.json` retained with the same GitHub
   release. A locally built synthetic candidate does not acquire a release
   attestation merely by following this guide. In a checkout, use:

   ```sh
   uv run make release-attestation-verify \
     ARTIFACT=/approved/project/rareburden-<version>-py3-none-any.whl \
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
5. Preinstall Python and `uv` before the measured phase. For the synthetic
   rehearsal, invoke the script with the already provisioned Python directly
   from the pinned checkout; an outer `uv run` could synchronize an environment
   before the offline checks start. Replace the example paths and version with
   the exact recorded artifacts:

   ```sh
   python scripts/check_offline_node_install.py \
     --node-wheel /candidate/project/rareburden-<version>-py3-none-any.whl \
     --wheelhouse /candidate/dependency-wheelhouse \
     --python-version 3.13
   ```
   This creates and removes its own clean temporary environment and runs the
   installed synthetic aggregate fixture from an unrelated directory. Retain
   successful JSON stdout, command, timestamp, exit status and actual runtime
   identity outside the wheelhouse. Failed commands are not successful receipts.
   The receipt's `network_disabled` flag describes package-command configuration,
   not proof of OS-level isolation. Its `python_version` is the requested
   selector, not an observed patch-version attestation.
6. `uv run make installed-package-check` is an optional broader packaging check;
   it may fetch dependencies and is not an offline-install substitute.
7. Run `uv run make node-reproducibility` for two in-memory synthetic executions.
   This checks deterministic output, not packaging or separate installation.
8. Run an explicitly synthetic cohort through
   `aggregate_synthetic_records`, register its value-free query shape in a
   `QueryLedger` snapshot, then pass the resulting aggregate rows to
   `run_offline_node`.
9. Inspect suppression statuses and confirm no participant fields are present.
10. Retain the verification receipt, execution manifest and environment identity
    with the review packet.
11. For a correction, `amend_execution_manifest` creates a new prepared record
    with a new execution ID; it does not rerun analysis or certify corrected
    output. Preserve the original record.
12. For withdrawal, retain a separate status/disposition and stop distribution.
    There is no withdrawal CLI or automatic remote recall; changing a manifest
    does not retract already distributed copies.

## Rejection and recovery

| Failure or observation | Required response |
|---|---|
| Missing interpreter/dependency or attempted download | Stop the measured run. Repair staging in the preparation phase and record a new rehearsal; do not enable network fallback. |
| Wheel, bundle or output hash mismatch | Quarantine the candidate, retain the failure and reconcile exact artifacts before rerunning or distributing. |
| Incompatible version, missing field, identifier or nested participant value | Reject the input. Correct only the invented fixture/contract under review; never strip real identifiers to bypass validation. |
| Weaker policy, replay, query-budget rejection or missing history | Stop. Do not reset the ledger or lower thresholds to force success. Resolve policy/history under the applicable authority. |
| Suppressed or absent output | Treat it as unavailable, not zero; do not repeat or combine queries to infer hidden cells. |

Inspect evidence before public retention: no credentials, participant values,
controlled source bytes, host paths or raw failure logs. Successful installation
is engineering evidence, not permission to use data or a production service.

If installation needs network access, a schema check fails, a query-history receipt
is unavailable, or a fingerprint differs, stop without exporting and record the
failure for engineering and custodian review.

No operator may connect a node to a custodian, lower disclosure thresholds, or
publish an output without the applicable governance and export-review approvals.
The in-memory policy/ledger and SQLite reference store do not themselves establish
custodian ownership, access control, backup or production authority.
