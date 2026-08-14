# Track 014 plan

> Repository-owned review uses the subagent panel under ADR-0008; release, rights, accessibility and independent reproduction gates remain separate.

## Phase 1 — Product and information design

- [ ] Define user journeys for patient, policy, research, custodian and funder users.
- [ ] Define atlas pages, data package and API contracts. `[C-01]`
- [ ] Define provenance, uncertainty, quality and missingness components.
- [ ] Complete accessibility design review. `[M-23]`

## Phase 2 — Release contracts

- [ ] Define release-manifest and public-output schemas.
- [ ] Implement reviewed-artifact-only build boundary.
- [ ] Implement citation, licence, checksum and provenance packaging.
- [x] Implement correction, withdrawal and supersession metadata. Evidence:
  `rareburden.atlas.build_atlas_release_notice`,
  `rareburden.atlas.build_atlas_release_status`,
  `schemas/atlas-release-status.schema.json` and lifecycle negative tests create
  immutable, hash-bound, accessible fail-closed status projections without
  authorizing publication.

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

## Preparation refresh — 2026-08-01

- [x] Prepared `docs/track-014-atlas-api-review-packet.md` with exact
  source-rights, semantic, accessibility, reproducibility and release-authority
  evidence requests.
- [ ] Keep atlas/API publication disabled until upstream review and accountable
  dispositions are complete.

## Implementation planning — 2026-08-02

- [x] Add the dependency-ordered atlas/API implementation plan with options,
  contingencies and recommendation in
  `docs/track-014-implementation-plan-2026-08-02.md`.
- [x] Implement the recommended static-first reviewed-release slice. Evidence:
  `rareburden.atlas.build_atlas_release_candidate`,
  `schemas/atlas-release-surface.schema.json`, and release-surface tests bind
  aggregate package/API parity, reviewed-artifact receipts, rights disposition,
  citation and provenance while keeping publication explicitly unauthorized.
- [x] Implement the metadata-only static-first gap-product slice. Evidence:
  `generate-gap-map`, `src/rareburden.gapmap.render_gap_map_markdown`, and
  `tests/test_gapmap.py` produce schema-valid accessible Markdown/JSON with
  explicit missingness, readiness and limitations; no API or beta publication
  is enabled.
- [x] Project the same release into a versioned aggregate package and read-only
  API with parity checks. Evidence: package, API and prepared release-surface
  fingerprints are tested together; no network service or publication is enabled.
- [x] Implement the versioned aggregate gap-package projection. Evidence:
  `rareburden.atlas.build_gap_package` and `tests/test_atlas_package.py` bind
  package identity to a source manifest, preserve missingness and enforce
  aggregate-only output; API projection and publication remain open.
- [x] Implement a read-only API-shaped gap projection with package-fingerprint
  parity checks in `rareburden.atlas.build_gap_api_response` and
  `tests/test_atlas_package.py`; no network server or publication is enabled.
- [x] Add a schema and synthetic parity test for the read-only response in
  `schemas/atlas-api-response.schema.json` and `tests/test_atlas_api_schema.py`.
- [x] Add the bounded accessibility and disclosure checklist in
  `docs/track-014-accessibility-checklist.md` with a regression guard; independent
  accessibility/community review remains pending.
- [x] Add deterministic correction, withdrawal and supersession status metadata
  shared by static and API consumers. Notices bind the affected candidate,
  require a different exact replacement for corrections/supersessions, reject
  tampering and expose a text alternative; repository state remains unpublished.
- [ ] Complete accessibility, independent-operator and release-authority gates
  before beta publication.
