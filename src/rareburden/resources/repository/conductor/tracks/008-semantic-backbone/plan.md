# Track 008 plan

> Repository-owned review uses the subagent panel under ADR-0008; clinical and patient/community semantic authority remains separate.

## Phase 1 — Contracts and source releases

- [x] Define disease-definition and mapping schemas. `[M-01, M-02, M-18]`
  Evidence: ontology-mapping and hierarchy schemas with strict semantic tests;
  source release approval remains open.
- [ ] Pin source ontology/coding releases and licence states.
- [x] Define stable internal identifiers and mapping provenance. Evidence:
  mapping schemas require stable entity IDs, source/version and evidence refs.
- [x] Define ambiguity, deprecation and migration representation. Evidence:
  relation enums, validity fields and deterministic mapping-diff receipts.

## Phase 2 — Burden-purpose hierarchy

- [x] Create supported demonstrator entity sets. Evidence: synthetic
  monogenic, bronchiectasis and paediatric semantic fixtures.
- [x] Define mutually exclusive aggregation nodes and non-tree relationships. `[M-05, S-02]` Evidence: hierarchy conservation and aggregation-contract tests.
- [x] Define syndrome/aetiology and multi-diagnosis rules. Evidence: explicit
  relation and aggregation contracts in synthetic hierarchy fixtures.
- [ ] Obtain clinical and patient/community naming review.

## Phase 3 — Implementation

- [x] Implement mapping loader, query and version-diff tooling. Evidence: validated `diff_mapping_sets` release impact report and focused tests in `d93d55e`; source-release pinning remains external-gated.
- [x] Add hierarchy conservation, parent/child and ambiguity tests. Evidence: `2e5224c`; golden demonstrator conservation tests cover the supported synthetic hierarchies.
- [x] Add golden fixtures for monogenic diabetes, bronchiectasis and paediatric use. Evidence: `2e5224c`; all fixtures are synthetic and non-clinical.
- [x] Generate machine-readable and human-readable semantic releases from
  validated synthetic inputs. Evidence: `examples/semantics/orpha-to-synthetic-mapping.yml`
  and its deterministic rendered companion under
  `examples/semantics/releases/`; source-pinned production generation remains
  blocked until Track 002 source terms and semantic authority are approved.

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

## Repository-owned release preparation — 2026-08-03

- [x] Implement deterministic human-readable semantic-release rendering for
  validated synthetic mappings in `rareburden.semantics` with limitation
  disclosure; production source-pinned release remains open.
