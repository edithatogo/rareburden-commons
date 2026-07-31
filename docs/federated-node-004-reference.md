# Track 004 federated-node reference

The first local node primitive is `validate_aggregate_export`. It rejects
participant-level identifiers, requires non-negative integer counts, and marks
cells below the configured minimum as suppressed rather than releasing a value.
The primitive is offline and deterministic; it does not connect to a custodian,
execute a person-level query, or override local disclosure policy.

`rareburden.node.run_offline_node` composes this boundary with a completed
synthetic execution manifest. It returns only the manifest and disclosure-safe
rows, with no network, persistence, or controlled-data access.

Corrections use `amend_execution_manifest`, which creates a superseding record
without mutating the original. `redact_node_log` removes credentials and
participant identifiers from nested diagnostic metadata.

The bounded validator compares analysis overrides with a supplied custodian
baseline, accepts only approved aggregate dimensions, rejects nested export
values, and applies a supplied-history replay/overlap-group guard. These are local
comparison primitives; authoritative policy loading and durable query-ledger
enforcement remain part of the approved common runner. Completed manifests include
a canonical SHA-256 digest that can be recomputed with
`verify_output_fingerprint`.

The synthetic node contract still requires execution-manifest, version
negotiation, environment capture, correction/withdrawal handling and independent
security/data-governance review before any controlled pilot or node alpha claim.
