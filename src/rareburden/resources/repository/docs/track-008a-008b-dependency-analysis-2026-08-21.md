# Prospective Track 008A/008B dependency analysis

## Status

This is a scope-change candidate, not an implemented split. Track 008 remains
blocked, Track 009 remains blocked and inactive, and no completion or external
authority is inferred.

## Proposed identities

- **008A** retains canonical ID `008-semantic-backbone` and would become the
  bounded non-clinical semantic infrastructure track.
- **008B** would use the schema-compatible canonical ID
  `019-clinical-community-semantic-assurance` and would hold attributable
  clinical, community, independent-review, extended-source and derivative-use
  obligations.

The existing numeric ID is retained for 008A to avoid silently invalidating
historical manifests and downstream references. The 008B alias is descriptive;
the repository metadata schema requires three-digit numeric canonical IDs.

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

If the split is later approved, Track 009 would need a machine-enforced
mode-specific dependency contract:

- synthetic and non-clinical preparation may depend on completed 008A, while
  empirical activation, clinical use, patient-facing output and authority
  claims remain prohibited;
- any empirical or public semantic mode must also require completed 008B;
- any Track 008A, Track 008B or evidence-hash drift invalidates the affected
  downstream mode and requires a new panel and owner decision.

## Risks and contingencies

- A same-ID narrowing could be mistaken for completion of the original Track
  008 contract. Titles, release notes and dependency gates must identify 008A's
  bounded non-clinical scope wherever completion is later considered.
- Current evidence does not itself clear publication of extracted mapping or
  label derivatives. Such outputs must remain non-activated or private unless
  exact derivative-use evidence is recorded.
- Simulated panels cannot become patient/community participation, clinical
  validation, rights-holder permission or independent review.
- If the final panel rejects same-ID narrowing, create two new successor IDs and
  leave Track 008 blocked as the historical umbrella.

## Required final evidence

Before implementing the split, require a schema-valid simulated-panel packet
bound to the exact scope candidate, options with trade-offs and contingencies,
an explicit owner disposition, a complete requirement-transfer matrix, new
specifications and metadata, mode-specific dependency tests, runtime-mirror
synchronization, and hosted Python 3.12–3.14 checks.
