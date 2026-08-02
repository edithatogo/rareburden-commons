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
- [ ] Implement the recommended static-first reviewed-release slice.
- [ ] Project the same release into a versioned aggregate package and read-only
  API with parity checks.
- [ ] Complete accessibility, independent-operator and release-authority gates
  before beta publication.
