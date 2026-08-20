# Owner disposition — Option B bounded preparation

**Decision date:** 2026-08-20  
**Decision owner:** repository owner  
**Status:** accepted for reversible repository preparation; no empirical or release gate closed

## Decision

The repository owner accepts **Option B — dependency-ordered dual-lane
preparation**. Reversible, clearly labelled synthetic preparation and
cross-cutting security engineering are authorised while the semantic, ledger
and burden-engine contract freezes remain serial:

1. Track 008 semantic contract;
2. Track 009 ledger/data contract;
3. Track 010 burden-engine alpha interface.

Downstream work may exercise provisional interfaces, synthetic fixtures,
negative controls, disclosure protections, threat models, dependency and secret
checks, recovery procedures, documentation and reviewer packets. It must remain
reversible and must not be used as completion evidence for an upstream track.

## Gates preserved

Empirical activation and all attributable human/community, custodian, clinical,
independent-review, quality, archival and release gates remain blocked until
their required accountable evidence exists. Source licences, third-party
rights, controlled-data policies and registry events remain factual constraints
that repository work cannot manufacture.

Role-separated panel outputs are advisory. This disposition is
**owner-operated governance, not independent review**. It does not establish
community authority, custodian approval, clinical approval, semantic validity,
empirical validity, archival acceptance or release authority.

## Stop and rollback rules

- A critical safety, rights, semantic-integrity, privacy, security,
  reproducibility or recovery finding stops the affected lane.
- An upstream contract change invalidates dependent provisional interfaces and
  requires revalidation before further preparation.
- Any artefact lacking an explicit synthetic/public-only classification fails
  closed and cannot enter a release candidate.
- If an accountable gate remains unavailable, narrow or defer the affected
  capability rather than infer approval.
