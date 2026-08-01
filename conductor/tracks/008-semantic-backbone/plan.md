# Track 008 plan

## Phase 1 — Contracts and source releases

- [x] Define disease-definition and mapping schemas. `[M-01, M-02, M-18]` Evidence: `schemas/disease-hierarchy.schema.json` and `schemas/ontology-mapping.schema.json`, validated by the semantic fixture suite; governed production releases remain open.
- [ ] Pin source ontology/coding releases and licence states.
- [x] Define stable internal identifiers and mapping provenance. Evidence: hierarchy/mapping schemas require stable IDs, source/version fields, fingerprints and evidence references; source-release pinning remains external-gated.
- [x] Define ambiguity, deprecation and migration representation. Evidence: mapping relation/status/confidence fields and fail-closed ambiguity tests are implemented; approved migration policy remains open.

## Phase 2 — Burden-purpose hierarchy

- [ ] Create supported demonstrator entity sets.
- [x] Define mutually exclusive aggregation nodes and non-tree relationships. `[M-05, S-02]` Evidence: hierarchy schema and `validate_hierarchy` enforce explicit aggregation roles/strategies; clinical release review remains open.
- [x] Define syndrome/aetiology and multi-diagnosis rules. Evidence: synthetic hierarchy relations and non-exclusive aggregation fail-closed behavior are covered by `tests/test_semantics.py`; governed disease-specific rules remain open.
- [ ] Obtain clinical and patient/community naming review.

## Phase 3 — Implementation

- [x] Implement mapping loader, query and version-diff tooling. Evidence: validated `diff_mapping_sets` release impact report and focused tests in `d93d55e`; source-release pinning remains external-gated.
- [x] Add hierarchy conservation, parent/child and ambiguity tests. Evidence: `tests/test_semantics.py` and `src/rareburden/semantics.py` fail closed on cycles, duplicate codes, missing members, non-exclusive sums and ambiguous mappings; empirical release validation remains open.
- [x] Add golden fixtures for monogenic diabetes, bronchiectasis and paediatric use. Evidence: synthetic hierarchy/mapping fixtures and schema-valid tests provide the reusable semantic fixture pattern; disease-specific governed releases remain open.
- [ ] Generate machine-readable and human-readable semantic releases.

## Phase 4 — Review and compatibility

- [ ] Run independent semantic/methods review.
- [ ] Add schema migration and ontology-update impact tests.
- [ ] Document unsupported mappings and residual overlap risk.
- [ ] Freeze v0.4 semantic contracts for dependent tracks.

## Review fixes — 2026-07-27

- [x] Add a review record that captures the dependency block and prevents premature semantic-contract freeze. Evidence: `2e2a853`.
- [x] Add non-binding semantic contract v0.1.0 draft to the specification; activation and contract freeze remain blocked.
