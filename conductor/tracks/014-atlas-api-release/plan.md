# Track 014 plan

## Phase 1 — Product and information design

- [ ] Define user journeys for patient, policy, research, custodian and funder users.
- [ ] Define atlas pages, data package and API contracts. `[C-01]`
- [ ] Define provenance, uncertainty, quality and missingness components.
- [ ] Complete accessibility design review. `[M-23]`

## Phase 2 — Release contracts

- [ ] Define release-manifest and public-output schemas.
- [ ] Implement reviewed-artifact-only build boundary.
- [ ] Implement citation, licence, checksum and provenance packaging.
- [ ] Implement correction, withdrawal and supersession metadata.

## Phase 3 — Atlas and API

- [ ] Build static demonstrator, country and gap products.
- [ ] Build versioned aggregate data package and API.
- [ ] Add consistency tests across static, package and API outputs.
- [ ] Add documentation and accessible text alternatives.

## Phase 4 — Reproducible release

- [ ] Add immutable archive/DOI and research-object workflow. `[S-09]`
- [ ] Build and verify from a clean environment.
- [ ] Complete independent reproduction and release-content audit.
- [ ] Publish v0.8 beta only after Track 013 approval.

## Preparatory dependency review — 2026-07-29

- [x] Document the immutable reviewed-artifact boundary, missingness rule,
  aggregate-only publication boundary and shared release-fingerprint requirement.
  Evidence: `docs/atlas-release-014-reference.md`; product activation remains
  blocked by upstream tracks and release gates.

## Preparatory implementation — 2026-08-01

- [x] Define the immutable release-manifest and aggregate-only public-output
  boundary. Evidence: `schemas/release-manifest.schema.json`,
  `src/rareburden/release.py`, and `docs/atlas-release-014-reference.md`.
  This is a repository-owned contract; it is not a reviewed beta release.
- [x] Verify release materials by content hash, repository state and manifest
  identity before publication. Evidence: `verify_release_manifest` and the
  release negative tests in `tests/test_release.py` and
  `tests/test_quality_edges.py`.
- [x] Preserve provenance and research-object integrity for the offline
  reference workflow. Evidence: `src/rareburden/research_object.py`,
  `src/rareburden/reference.py`, and the assurance-boundary tests. External
  source rights and release authority remain open.
