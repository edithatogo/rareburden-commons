# Track 004 federated-node reference

The first local node primitive is `validate_aggregate_export`. It rejects
participant-level identifiers, requires non-negative integer counts, and marks
cells below the configured minimum as suppressed rather than releasing a value.
The primitive is offline and deterministic; it does not connect to a custodian,
execute a person-level query, or override local disclosure policy.

The synthetic node contract still requires execution-manifest, version
negotiation, environment capture, correction/withdrawal handling and independent
security/data-governance review before any controlled pilot or node alpha claim.
