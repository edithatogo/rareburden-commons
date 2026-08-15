# Track 014 dependency review — Atlas, API and reproducible release engineering

**Review date:** 2026-07-29  
**Decision:** Planned; implementation entry blocked by upstream release evidence

## Findings

- Tracks 002, 009, 010 and 013 are not complete, so no reviewed aggregate release
  exists for an atlas or API build.
- Local release-manifest, provenance, lineage and reproducibility primitives are
  available, but no public product or mutable dashboard has been activated.
- Scientific, patient/community, data-governance, security, accessibility and
  release gates remain required.

## Local preparation

`docs/atlas-release-014-reference.md` records the immutable reviewed-artifact
boundary, missingness rule, aggregate-only publication boundary and shared
release-fingerprint requirement. It is preparatory documentation, not a beta
release or publication authorization.

## Required gates before activation

- Track 013 approval of quality, equity and gap-map outputs.
- Reviewed source/parameter manifests and a release-content audit.
- Accessible static/API consistency tests and independent reproduction.
- Release authority approval for archive/DOI and public publication.

## Preparation refresh — 2026-08-01

`docs/track-014-atlas-api-review-packet.md` now records the exact evidence and
accountable decisions required for the reviewed-artifact boundary, public
output rights, semantic/accessibility controls, consistency, independent
reproduction and release. This is non-binding preparation; no atlas, API,
beta, archive or DOI has been activated.

## Repository-owned release-surface review — 2026-08-15

The static-first bounded slice now produces a schema-valid prepared release
surface only when the aggregate package and read-only API projection agree and
every input artifact carries an exact digest, repository review receipt and
explicit redistributable or metadata-only disposition. Negative tests reject
projection drift, unresolved rights, missing receipts and invalid digests.

This closes the repository-owned construction task only. Accessibility,
independent reproduction, upstream scientific/governance dependencies, release
authority, archive/DOI creation and public beta activation remain pending.

## Repository-owned lifecycle-metadata review — 2026-08-15

The prepared surface now has a deterministic correction, withdrawal and
supersession representation. Each notice binds the exact affected surface,
preserves the original candidate, requires an exact different replacement for
correction or supersession, forbids an implied replacement on withdrawal, and
is revalidated before projection. Static and API consumers can use the same
schema-valid status object and text alternative. Tampering, cross-candidate
notices, duplicate identifiers and ambiguous lifecycle transitions fail closed.

This is repository lifecycle evidence only. It does not show that a public
release was corrected or withdrawn, and it does not satisfy accessibility,
independent reproduction, upstream authority or release-authority gates.

## Bounded Track 008–013 reconciliation — 2026-08-16

Repository review result: **Pass for a local synthetic/static projection**.
The static model, aggregate package, read-only API shape and lifecycle status
share exact identifiers, preserve missingness and `not_assessed` sufficiency,
and remain publication-unauthorized. A withdrawal propagates `do_not_use` and
an accessible text alternative without mutating the candidate. Negative tests
reject dependency drift, surface mismatch, sufficiency upgrades and release
overclaims.

Track 014 remains **planned and non-public**. Accessibility, real-source
activation, separately executed reproduction, release authority and explicit
public/stable release decisions remain pending.
