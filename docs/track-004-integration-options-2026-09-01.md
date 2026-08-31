# Track 004 integration options — 2026-09-01

Status: **UNSELECTED proposal; owner decision pending.** No integration is
implemented or authorised by this document. Agents recommend; the repository
owner selects. Track 004 remains Blocked under its unchanged specification.

## Existing capability and the missing connection

- `aggregate_synthetic_records` (`src/rareburden/node_analysis.py`) counts
  explicitly synthetic records using allowlisted dimensions and deterministic
  multi-diagnosis groups. It does not reserve a durable query budget.
- `run_offline_node` (`src/rareburden/node.py`) applies an offline aggregate
  export boundary, supplied policy limits and supplied query history, returning
  rows and a manifest in memory. It does not load an authoritative policy store.
  Its aggregate-input fingerprint includes numeric counts.
- `DurableNodePolicyStore.register_query` (`src/rareburden/node_policy_store.py`)
  verifies stored policies/history and registers value-free query receipts under
  a SQLite write transaction. It does not accept an operator-pinned expected
  policy hash or return the exact policy snapshot for downstream suppression.
  There is no integrated orchestration of reservation, aggregation and export.

Source paths above require the full repository checkout, not the installed
documentation projection. These are reference primitives, not a production
common analysis contract or a custodian-authorised deployment. Existing
installation receipts apply to their
bound candidates, not automatically to a future integrated candidate. See the
[review packet](track-004-node-review-packet.md) and
[Track 004 plan](../conductor/tracks/004-federated-node-runner/plan.md).

## Option A — bounded synthetic integration (recommended)

Selection would authorise an additive, experimental synthetic-only orchestration
prototype and its tests, not production-contract freeze, Track 004 completion,
controlled-data activation or release. Use only explicitly invented inputs;
`synthetic: true` is not de-identification or evidence that real records are safe.
No source acquisition, real-data acceptance or empirical analysis is included.

### Proposed execution contract

1. Receive operator-supplied policy ID and expected policy SHA separately from
   the analysis request. Bind the permitted analysis identity and overlap-group
   identity separately too; the request cannot substitute these identities.
   These are local operator assertions, not authenticated custodian credentials.
2. Copy/freeze the query and effective execution inputs before validation. Bind
   that same query to the executed dimensions and analysis; do not validate one
   mutable object and subsequently execute another. Preflight supported versions,
   request shape, identifiers and input structure without aggregating. Perform
   policy-dependent preflight under the transaction in step 3, before commitment.
3. Inside the query-registration write transaction, verify store integrity and
   compare the stored policy ID/hash with the operator's expected values. Require
   `aggregate_only` policy export mode, reject weaker overrides and unapproved
   dimensions, and enforce replay/overlap-budget checks against the frozen query.
   Return the exact immutable policy snapshot used for that reservation, not a
   later lookup or caller-supplied approximation. A preliminary lookup alone is
   insufficient.
4. Commit the value-free query reservation **before aggregation or any result**.
   Failed commit means no aggregation and no result. A pre-commit rejection
   produces no result and no committed reservation. If commit success is
   uncertain, stop without analysis or an automatic retry.
5. Aggregate the frozen invented inputs, then apply suppression and export
   validation using the exact returned policy. Never reload a different policy,
   fall back to defaults or weaken the reserved controls. After a successful
   commit, any aggregation, validation or result-construction failure consumes
   that reservation; no automatic retry, refund, budget reset or replacement
   store is permitted. A rejected result is not returned partially.
6. Return the validated aggregate result in an experimental in-memory envelope
   binding the committed receipt sequence, chain and query identity, reserved
   policy ID/SHA, and execution/output identity. Reject mismatched bindings;
   this is consistency metadata, not signed proof of execution or delivery.
   Preserve the existing result contract inside that envelope. Keep value-free
   query-shape identity, numeric aggregate-input fingerprint and output fingerprint
   distinct. Numeric input hashes do not replace query-shape budget identity.
   Persist no participant values or numeric aggregates in the query receipt.

No filesystem output/publication or atomic file-delivery state machine is
proposed. The durable fact is reservation, not successful execution or delivery.
Suppressed values remain suppressed, not zero; outputs must not imply complete
coverage or disclosure guarantees merely because they passed this boundary.

### Minimum acceptance tests for a future implementation

- Missing/wrong policy ID or expected hash fails before aggregation or result.
- Policy tampering or a policy change between preliminary lookup and reservation
  cannot bypass the transaction-bound hash check.
- Malformed, unavailable or tampered stores fail closed without a fallback store.
- Replay rejection and overlap budgets survive close/reopen; competing
  registrations cannot both spend the same remaining budget.
- An injected commit failure prevents aggregation and result creation; ambiguous
  commit outcomes do not trigger a retry or assumption that budget is unspent.
- Injected post-commit aggregation, export-validation and result-construction
  failures return no result and leave the reservation consumed after reopening.
- Weaker requested controls are rejected; the exact policy returned by the
  reservation governs suppression and allowlists even if another lookup differs.
- Caller mutation cannot alter the frozen query, inputs or effective controls;
  request identities cannot override the operator-bound analysis/overlap IDs.
- Unsupported export modes, incompatible versions, invalid input structure and
  identifier fields are rejected before analysis; no partial result is exposed.
- Different numeric aggregate inputs do not silently redefine the value-free
  query shape or evade its replay/budget constraints. Receipt inspection confirms
  no numeric aggregate or raw-record values are persisted.
- Valid invented inputs yield deterministic schema-valid aggregate results, with
  no raw-record leakage and suppression distinguishable from zero.
- Returned result/receipt/policy bindings agree; substituted receipt sequence,
  chain/query identity, policy ID/SHA or execution/output identity is rejected.
- Existing public APIs, fixtures and historical receipt bytes remain unchanged;
  new tests exercise the additive prototype rather than relabel old evidence.

### Trade-offs and contingencies

A connects already-tested primitives and makes failure behaviour testable without
choosing a production trust root. Reserving before work conservatively spends
budget even when no result is delivered; this is intentional, not exactly-once
execution. Caller-chosen identities, local database reset/replacement and a
privileged local actor still limit the security claim. It does not guarantee
protection against differencing, establish custodian authority or certify safety.

If the frozen query cannot be bound to execution, the reserved policy cannot be
returned unchanged, or commit outcome is uncertain, stop rather than improvise a
retry/recovery policy. Recovery, identity administration and production export
delivery need separate design and disposition. Advisory agents do not substitute
for actual participation, permissions or custodian policy.

## Option B — production-contract candidate preparation only

Selection would authorise a documented candidate contract and unresolved-input
register, not implementation, deployment or activation. Specify the common
analysis interface, identities, policy authority, durable-store ownership/access
controls, backup/recovery, supported platforms, export disposition and accepted
artifact-verification trust inputs. Identify which inputs require actual
custodian policies, rights/access permissions and deployment identities; do not
invent them or treat a software hash as permission.

Acceptance would be a traceable candidate with failure cases, evidence required
for each trust assumption and a further exact owner decision before any proposed
implementation. Actual permissions remain necessary where applicable. This
option addresses production design uncertainty but cannot close missing external
facts. If those facts are unavailable, retain explicit unknowns and stop there.
No new analysis, signed output package or production security claim is included.

## Option C — defer integration

Retain current primitives, tests and installation evidence without a new runner.
Record the deferred choice and conditions for reconsideration. This avoids a new
experimental interface but leaves the integration gap untouched; it is not
completion or a waiver of acceptance criteria.

## Unchanged completion boundary

All six original plan gates remain pending under every option: rights/data-use
and community/harm advisory challenge with owner disposition; production common
analysis contract and approved locked dependencies; authoritative custodian-store
binding; separately recorded clean-environment installation/run with challenge
and owner disposition; final methods/privacy/security/engineering challenge and
owner disposition; and node-alpha release after blocking findings close.

Green prototype tests would not close these gates automatically. A later desire
to complete Track 004 on synthetic-only scope requires an explicit scope
amendment and acceptance mapping, not reinterpretation of Option A. No actual
community participation, independent review, custodian approval or release is
claimed by preparing, reviewing or selecting this proposal.
