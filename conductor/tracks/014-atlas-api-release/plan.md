# Track 014 plan

## Phase 1 — Product and information design

- [ ] Define user journeys for patient, policy, research, custodian and funder users.
- [ ] Define atlas pages, data package and API contracts. `[C-01]`
- [ ] Define provenance, uncertainty, quality and missingness components.
- [ ] Complete accessibility design review. `[M-23]`

## Phase 2 — Release contracts

- [x] Define release-manifest and public-output schemas. Evidence: existing
  `schemas/release-manifest.schema.json` plus the synthetic static/package/API
  consistency fixture and contract in `docs/atlas-release-014-reference.md`;
  activation remains gated.
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
