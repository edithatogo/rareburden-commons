# Prospective Track 008A/008B dependency analysis

## Status

This is a scope-change candidate, not an implemented split. Track 008 remains
blocked, Track 009 remains blocked and inactive, and no completion or external
authority is inferred.

## Proposed identities

- Historical `008-semantic-backbone` remains a blocked umbrella unless an exact
  supersession candidate is later approved.
- **008A** would use `019-bounded-semantic-infrastructure`.
- **008B** would use `020-clinical-community-semantic-assurance` and hold attributable
  clinical, community, independent-review, extended-source and derivative-use
  obligations.

Distinct successor IDs prevent a future bare `Track 008 complete` status from
being mistaken for satisfaction of the historical clinical/community contract.
They require an explicit reference migration, which is analysed but not enacted here.

## Requirement transfer

008A would retain schemas, stable identifiers, explicit ambiguity, the bounded
provisional mapping and naming artifacts, hierarchy and overlap controls,
migration/deprecation behavior, synthetic fixtures and deterministic tooling.

008B would receive the unmet obligations that repository metadata and simulated
panels cannot satisfy: attributable patient/community naming and aggregation
review, clinical mapping fitness, independent semantic review, extended-source
decisions, and field-level derivative-publication rights.

The historical Track 008 specification, plan, review and owner decisions remain
unchanged until a final exact-candidate decision. A later implementation must
record the transfer prospectively rather than rewriting the historical record.

## Track 009 effects

The preparation candidate makes **no dependency change**. Track 009 remains
blocked on canonical Track 008 and cannot infer satisfaction from the bounded
v0.4 freeze or this proposal.

If the split is later approved, Track 009 and every inventoried consumer would
need an atomic, machine-enforced mode-specific dependency contract:

- synthetic internal preparation may depend on completed 008A, while
  empirical activation, clinical use, patient-facing output and authority
  claims remain prohibited;
- exact unmodified source assets additionally require their source-specific route;
- any source-derived, empirical, public-facing, clinical, patient-facing or
  authority-bearing mode must also require completed 008B and exact evidence;
- any Track 008A, Track 008B or evidence-hash drift invalidates the affected
  downstream mode and requires a new panel and owner decision.

## Risks and contingencies

- Successor IDs create migration work, but preserve the meaning of historical
  Track 008 and prevent generic dependency satisfaction.
- The mapping and naming derivatives already occur in public Git history; they
  are not confidential or private. That exposure does not clear rights,
  activation, republication, rendering or external product use. The exact
  hash-identified artifacts are proposed for no additional repository-owned
  publication, export, rendering, activation or promotion until an exact
  derivative-use disposition is recorded. Historical Git availability persists;
  this proposal cannot retract prior distribution.
- Simulated panels cannot become patient/community participation, clinical
  validation, rights-holder permission or independent review.
- The transfer matrix accounts individually for eight required outputs, seven
  acceptance criteria, the protocol review gate and both v1 contributions.

## Required final evidence

Before implementing the split, require a schema-valid simulated-panel packet
bound to the exact scope candidate, options with trade-offs and contingencies,
an explicit owner disposition, a complete requirement-transfer matrix, new
specifications and metadata, mode-specific dependency tests, runtime-mirror
synchronization, and hosted Python 3.12–3.14 checks.
