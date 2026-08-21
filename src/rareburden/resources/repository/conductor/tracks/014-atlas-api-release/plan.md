# Track 014 plan

> Repository-owned review uses the subagent panel under ADR-0008; release, rights, accessibility and independent reproduction gates remain separate.

## Phase 1 — Product and information design

- [x] Define bounded user journeys for patient, policy, research, custodian and
  funder users. Evidence:
  `docs/track-014-bounded-user-journeys-2026-08-21.yml` and
  `tests/test_track014_user_journeys.py`. These are repository design
  hypotheses, not user research, endorsement or accessibility approval.
- [x] Define the bounded static page, aggregate data-package and read-only API
  contracts. Evidence: `schemas/atlas-static-projection.schema.json`,
  `schemas/atlas-api-response.schema.json` and
  `docs/track-014-bounded-reconciliation-2026-08-16.md`. These synthetic
  contracts do not activate a hosted API or public atlas. `[C-01]`
- [x] Define provenance, uncertainty, quality and missingness components.
  Evidence: `docs/track-014-evidence-presentation-contract-2026-08-21.yml`,
  `schemas/atlas-evidence-presentation-contract.schema.json`,
  `examples/atlas/evidence-presentation-fixtures.yml` and
  `tests/test_track014_evidence_presentation_contract.py` define one shared
  scientific-fact contract, five audience profiles and fail-closed synthetic
  scenarios. This is repository design evidence, not user research or
  independent accessibility approval.
- [ ] Complete accessibility design review. `[M-23]`

## Phase 2 — Release contracts

- [x] Define release-manifest and bounded output schemas. Evidence:
  `schemas/release-manifest.schema.json`,
  `schemas/atlas-release-surface.schema.json`,
  `schemas/atlas-static-projection.schema.json` and
  `schemas/atlas-api-response.schema.json`.
- [x] Implement reviewed-artifact-only build boundary. Evidence:
  `rareburden.atlas.build_atlas_release_candidate` and
  `tests/test_atlas_package.py` reject missing review receipts, unresolved
  licence states, invalid digests and package/API drift.
- [x] Implement bounded citation, licence, checksum and provenance packaging.
  Evidence: the release-surface contract requires citation/provenance IDs and
  hash-bound reviewed artifacts with explicit redistribution disposition. This
  is synthetic preparation, not public redistribution clearance.
- [x] Implement correction, withdrawal and supersession metadata. Evidence:
  `rareburden.atlas.build_atlas_release_notice`,
  `rareburden.atlas.build_atlas_release_status`,
  `schemas/atlas-release-status.schema.json` and lifecycle negative tests create
  immutable, hash-bound, accessible fail-closed status projections without
  authorizing publication.

## Phase 3 — Atlas and API

- [x] Build bounded static demonstrator, synthetic-country and gap products.
  Evidence: `rareburden.atlas.build_static_product_set`,
  `schemas/atlas-static-product-set.schema.json` and
  `tests/test_track014_static_product_set.py` generate three accessible,
  content-addressed product models from one immutable prepared package. The
  country identifier is restricted to the user-assigned `XAA`–`XZZ` range;
  every product remains synthetic, metadata-only and unpublished.
- [x] Build a versioned synthetic aggregate data package and read-only API
  projection. Evidence: `rareburden.atlas.build_gap_package`,
  `rareburden.atlas.build_gap_api_response` and `tests/test_atlas_package.py`.
- [x] Add consistency tests across static, package and API outputs. Evidence:
  `tests/test_track014_bounded_reconciliation.py` binds their exact release,
  package, surface and lifecycle identities and rejects drift.
- [x] Add bounded documentation and accessible text alternatives. Evidence:
  `docs/track-014-accessibility-checklist.md`, the static projection's
  `text_alternative`, and `tests/test_atlas_accessibility.py`. Independent
  accessibility and patient/community review remain pending.

## Phase 4 — Reproducible release

- [ ] Add immutable archive/DOI and research-object workflow. `[S-09]`
- [x] Build and verify from a clean environment. Evidence:
  `docs/track-014-owner-installed-reproduction-receipt-2026-08-22.json` records
  installed-wheel doctor, synthetic reference workflow and synthetic-node
  passes. The run is owner-operated and explicitly not independent reproduction.
- [ ] Complete owner-operated clean-environment reproduction and agent-panel release-content audit.
- [x] Prepare an exact-candidate, non-authorizing release-content audit packet
  that routes panel advice and unresolved gates to the accountable owner.
  Evidence: `docs/track-014-release-content-audit-preparation-2026-08-22.json`;
  the owner decision and all external gates remain pending.
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
- [x] Keep atlas/API publication disabled while upstream review and accountable
  dispositions are incomplete. Evidence:
  `manifests/atlas/track-014-bounded-release-surface-2026-08-16.json` and its
  validator require publication and release claims to remain false. This
  records the current invariant and does not authorize later activation.

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
- [ ] Complete accessibility-agent, owner-operated operator and repository-owner
  release gates before beta publication.

## Bounded downstream reconciliation — 2026-08-16

- [x] Bind exact Track 008–013 synthetic artifacts into a fail-closed release
  manifest with real-source, accessibility, reproduction, release-authority and
  public/stable release gates pending.
- [x] Implement a schema-valid static atlas projection sharing exact identity
  with the aggregate package, read-only API shape and lifecycle status.
- [x] Add deterministic dependency, parity, lifecycle and negative checks that
  reject hash drift, missingness/sufficiency upgrades, publication claims and
  cross-surface identity mismatch.
- [ ] Activate real sources or publish any beta/stable surface only after the
  remaining gates are satisfied for an exact candidate.

## Review fixes — 2026-08-22

- [x] Reject symlinked descendants when assigning logical paths to generated
  assurance artefacts. Evidence: `45dad19` retains the bounded runtime
  improvement while preventing a pre-existing output-directory symlink from
  escaping the declared artefact root; `tests/test_reference.py` exercises the
  fail-closed case.
