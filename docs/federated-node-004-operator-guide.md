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
8. For the selected experimental integration, use
   `rareburden.node_orchestration.run_reserved_synthetic_analysis` with an
   already opened `DurableNodePolicyStore`. This is a Python API, not a
   production node CLI. Supply `analysis_id`, `overlap_group`,
   `expected_policy_id` and `expected_policy_content_sha256` as operator-bound
   arguments; do not place `analysis_id` inside `query_shape` or derive these
   identities from the records. For example, with explicitly invented records
   and a policy already registered in the store:

   ```python
   from rareburden.node_orchestration import (
       run_reserved_synthetic_analysis,
       verify_reserved_synthetic_result,
   )

   envelope = run_reserved_synthetic_analysis(
       invented_records,
       store=store,
       query_shape={"dimensions": ["jurisdiction"], "measure": "count"},
       analysis_id="invented-analysis",
       overlap_group="invented-overlap-group",
       expected_policy_id="invented-policy",
       expected_policy_content_sha256=recorded_policy_sha256,
       recorded_at="2026-09-01T00:00:00Z",
       execution_id="invented-execution",
       coordinator_version="0.1.0",
       node_version="0.1.0",
   )
   verify_reserved_synthetic_result(envelope)
   ```

   Replace every example value with the exact reviewed synthetic candidate
   value. The function freezes and preflights the query and invented records,
   then commits the value-free reservation before aggregation. A pre-commit
   rejection returns no result and commits no reservation. Once committed, the
   reservation remains consumed if aggregation, export validation, result
   construction or binding verification fails. There is no automatic retry,
   refund, budget reset or replacement-store recovery. If commit success is
   uncertain, stop without analysis and do not retry: inspection and recovery
   need a separately approved procedure.

   The returned in-memory envelope binds the receipt sequence, query and chain
   fingerprints, exact policy ID/hash, execution ID and input/output
   fingerprints. These are consistency metadata, not a signature, execution
   attestation, delivery receipt or permission to distribute. This reference
   store is not an authoritative custodian system merely because the bindings
   verify.
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
| Expected policy ID/hash differs from the transaction-bound stored policy | Stop before analysis. Reconcile the operator-approved policy and store; do not substitute a caller-supplied policy or weaken controls. |
| Commit outcome is uncertain | Stop without analysis or automatic retry. Do not assume the reservation failed or that budget remains. Escalate for a separately approved inspection/recovery procedure. |
| Aggregation, export validation or result construction fails after commit | Return no partial result. Treat the reservation as consumed; do not refund, retry, reset the budget or replace the store. |
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

All six original Track 004 gates remain pending and the track remains blocked.
The selected synthetic prototype does not approve the production common-analysis
contract, create an authoritative custodian store, activate controlled data or
authorise node-alpha release. Historical installation or execution receipts do
not transfer to this changed orchestration candidate; any installation/run claim
needs a separately executed receipt bound to its exact commit, tree and artifacts.
