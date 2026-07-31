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
comparison primitives. `rareburden.node_policy` adds immutable, schema-aligned
policy snapshots and an immutable reference query ledger with stable value-free
query identities, replay rejection and overlap budgets. It is deliberately
memory-only: authoritative policy loading and durable custodian-controlled
query-ledger enforcement remain part of the approved common runner.

`rareburden.node_analysis.aggregate_synthetic_records` is a bounded common
analysis for explicitly synthetic records. It rejects identifier and unknown
fields and places overlapping diagnoses into exclusive canonical combination
buckets so each synthetic record contributes once. It is not approved for
controlled data.

`scripts/build_node_bundle.py` deterministically packages one project wheel and
locally supplied dependency wheels with canonical metadata and integrity checks.
It performs no downloads. A complete approved wheel set, clean second-operator
installation and supply-chain/signing review remain external gates.

Completed manifests include a canonical SHA-256 digest that can be recomputed with
`verify_output_fingerprint`.

The synthetic node contract still requires execution-manifest, version
negotiation, environment capture, correction/withdrawal handling and independent
security/data-governance review before any controlled pilot or node alpha claim.
