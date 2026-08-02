# Track 008 plan

> Repository-owned review uses the subagent panel under ADR-0008; clinical and patient/community semantic authority remains separate.

## Phase 1 — Contracts and source releases

- [ ] Define disease-definition and mapping schemas. `[M-01, M-02, M-18]`
- [ ] Pin source ontology/coding releases and licence states.
- [ ] Define stable internal identifiers and mapping provenance.
- [ ] Define ambiguity, deprecation and migration representation.

## Phase 2 — Burden-purpose hierarchy

- [ ] Create supported demonstrator entity sets.
- [ ] Define mutually exclusive aggregation nodes and non-tree relationships. `[M-05, S-02]`
- [ ] Define syndrome/aetiology and multi-diagnosis rules.
- [ ] Obtain clinical and patient/community naming review.

## Phase 3 — Implementation

- [x] Implement mapping loader, query and version-diff tooling. Evidence: validated `diff_mapping_sets` release impact report and focused tests in `d93d55e`; source-release pinning remains external-gated.
- [x] Add hierarchy conservation, parent/child and ambiguity tests. Evidence: `2e5224c`; golden demonstrator conservation tests cover the supported synthetic hierarchies.
- [x] Add golden fixtures for monogenic diabetes, bronchiectasis and paediatric use. Evidence: `2e5224c`; all fixtures are synthetic and non-clinical.
- [ ] Generate machine-readable and human-readable semantic releases from
  source-pinned inputs.

## Phase 4 — Review and compatibility

- [ ] Run independent semantic/methods review.
- [x] Add schema migration and ontology-update impact tests for synthetic
  mapping releases. Evidence: `tests/test_semantics.py` covers deterministic
  release diffs, added/removed/changed impact summaries and migration receipts;
  live ontology release pinning remains open.
- [x] Add deterministic migration-receipt fingerprint coverage. Evidence:
  `test_mapping_diff_binds_both_release_fingerprints`; source-release approval
  and clinical semantic authority remain external gates.
- [x] Prepare the release-content contract for future synthetic/source-pinned
  outputs. Evidence: `docs/track-008-semantic-review-packet.md` defines the
  machine-readable mapping, human-readable report, source IDs/hashes, licence,
  migration and residual-risk fields; generation remains blocked until source
  releases are approved.
- [x] Document unsupported mappings and residual overlap risk. Evidence:
  `docs/track-008-semantic-review-packet.md` records fail-closed handling for
  unmapped, ambiguous and deprecated relations plus explicit residual overlap;
  source-pinned semantic authority remains open.
- [ ] Freeze v0.4 semantic contracts for dependent tracks.

## Review fixes — 2026-07-27

- [x] Add a review record that captures the dependency block and prevents premature semantic-contract freeze. Evidence: `2e2a853`.
- [x] Add non-binding semantic contract v0.1.0 draft to the specification; activation and contract freeze remain blocked.

## Preparation refresh — 2026-08-01

- [x] Prepare the semantic review packet with decision fields, evidence links,
  release requirements and fail-closed continuation rules. Evidence:
  `docs/track-008-semantic-review-packet.md`; source-pinned release and external
  clinical/patient-community review remain blocked.
