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
