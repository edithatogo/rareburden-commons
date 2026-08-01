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

### Implementation checkpoint — 2026-08-01

The repository-owned release boundary was implemented and rechecked. Release
manifests are schema-constrained and content-addressed; verification rejects
manifest identity, repository-state and artefact-integrity mismatches. The
offline reference workflow and research-object checks preserve provenance and
do not activate an atlas, API, mutable dashboard, or public data publication.

Track 014 remains **Planned** rather than Active because its dependencies are
not complete. The atlas/API contracts, accessibility review, reviewed-artifact
inputs, independent reproduction, archive/DOI authority, and Track 013
approval remain release gates. No external approval or beta publication is
inferred from the local checks.

### Review rerun — 2026-08-01

The implementation checkpoint was reviewed against every acceptance criterion.
The local manifest, provenance, hash, research-object and clean-reference
checks are passing and the aggregate-only boundary is explicit. No defect was
found in the repository-owned slice.

The remaining findings are release-blocking scope, not fixable local defects:
the prerequisite tracks are incomplete; no reviewed aggregate release exists;
user journeys, API/package contracts, accessibility review, static/package/API
consistency, independent reproduction, archive/DOI authority and release
content audit are outstanding. Track 014 remains **Planned** and is not
archive-eligible. No atlas/API beta or public publication is authorised by
this review.
