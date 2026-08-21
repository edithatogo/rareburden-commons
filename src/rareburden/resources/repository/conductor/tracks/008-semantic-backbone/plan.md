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
- [ ] Obtain clinical-methods and community/harm naming challenge from agents and owner disposition.

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

- [ ] Run role-separated semantic/methods agent-panel review and owner disposition.
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

## Bounded gate preparation — 2026-08-03

- [x] Prepare the exact source-release/licence inventory with null-safe release,
  checksum, terms and redistribution fields. Evidence:
  `docs/track-008-source-release-inventory-2026-08-03.yml`; activation remains
  disabled until accountable dispositions are recorded.
- [x] Prepare the panel-assurance semantic/methods challenge packet with
  quorum, role separation, dissent, required outputs and stop triggers.
  Evidence: `docs/track-008-semantic-challenge-panel-2026-08-03.yml`.
- [x] Prepare the naming, grouping, accessibility and harm-review packet.
  Evidence: `docs/track-008-naming-harm-review-packet-2026-08-03.yml`.
- [x] Execute the repository panel challenge and record its bounded findings.
  Evidence: `docs/track-008-panel-assurance-report-2026-08-03.yml` and
  `docs/track-008-bounded-agent-review-2026-08-16.yml`. Both outputs are
  advisory; neither is owner disposition or independent review.
- [ ] Obtain clinical/community agent-panel naming recommendation and owner disposition.
- [ ] Pin approved source releases and confirm licence/redistribution terms.
- [ ] Freeze v0.4 semantic contracts only after all blocking findings and
  upstream Track 002/007 gates are closed.

## Bounded source reconciliation — 2026-08-16

- [x] Reconcile eight exact or bounded source-release records from current
  Track 002 receipts, including Orphadata, ORPHAcode, HPO, MONDO, UMLS,
  SNOMED CT and WHO ICD. Evidence:
  `docs/track-008-source-release-inventory-2026-08-03.yml` and
  `manifests/semantics/track-008-source-release-provenance-2026-08-16.json`.
  This does not complete the parent source-pinning task.
- [x] Enforce deterministic evidence hashing, public/private byte routing and
  fail-closed activation claims for the bounded source inventory. Evidence:
  `scripts/render_track008_source_provenance.py` and negative tests in
  `tests/test_track_008_gate_packets.py`.
- [x] Run a role-separated repository agent review of the reconciled inventory,
  naming boundaries and synthetic semantic fixtures. Evidence:
  `docs/track-008-bounded-agent-review-2026-08-16.yml`. This is not clinical,
  patient/community, custodian or independent approval, and its four medium
  findings remain bounded by disabled real-world mappings.
- [ ] Re-run the source and naming challenge after Track 002/007 completion,
  obtain the required owner disposition, and only then consider a v0.4 freeze.

## Option B preparation control — 2026-08-20

- [x] Record and machine-enforce the owner-authorised synthetic preparation
  boundary and serial Track 008 → 009 → 010 freeze order. Evidence:
  `docs/decisions/2026-08-20-owner-option-b-bounded-preparation.md`,
  `scripts/check_downstream_preparation.py` and focused negative tests. The
  semantic contract remains provisional and upstream, naming, clinical,
  community and review gates remain open.

## Freeze-readiness control — 2026-08-21

- [x] Encode the exact upstream, ontology-pin, naming/semantic finding and
  v0.4 freeze evidence required for Track 008 closure, with machine-enforced
  advisory-panel and owner-operated governance boundaries. Evidence:
  `docs/track-008-freeze-readiness-2026-08-21.yml`,
  `scripts/check_track_008_freeze_readiness.py` and focused negative tests.
  This is readiness preparation only; all parent blocking tasks remain open.

## Exact-candidate readiness — 2026-08-21

- [x] Bind the unchanged synthetic/public semantic substrate to its source
  commit, tree, artifact hashes and deterministic self-baseline migration
  receipt. Evidence:
  `manifests/semantics/track-008-provisional-candidate-2026-08-21.json`,
  `manifests/semantics/track-008-provisional-migration-impact-2026-08-21.json`
  and `docs/track-008-provisional-candidate-advice-2026-08-21.yml`. This packet
  is advisory readiness evidence only: source approval, naming authority,
  independent review, v0.4 freeze and Track 009 activation remain blocked.

## Post-upstream reconciliation — 2026-08-21

- [x] Reconcile the archived Track 002/007 outcomes into the bounded source
  inventory. Evidence: `docs/track-008-source-release-inventory-2026-08-03.yml`
  now binds the Track 002 owner disposition, recognizes only the exact
  Orphadata/MONDO allowlist, keeps HPO asset-specific, and leaves WHO and
  controlled sources disabled. This satisfies dependency ordering only; it
  does not establish mapping fitness, naming authority or freeze v0.4.

## Owner-approved v0.4 candidate preparation — 2026-08-21

- [x] Prepare the exact bounded v0.4 candidate using the approved Orphadata,
  MONDO and nine individually cleared HPO ontology-core objects; preserve typed
  uncertainty, non-clinical use, provisional owner-operated naming and all
  controlled or mixed-rights exclusions. Evidence:
  `manifests/semantics/track-008-v0.4-freeze-candidate-2026-08-21.json`,
  `manifests/semantics/track-008-v0.4-migration-impact-2026-08-21.json` and
  `docs/track-008-v0.4-candidate-challenge-2026-08-21.yml`, with the owner
  preparation decision in
  `docs/decisions/2026-08-21-track-008-v0.4-candidate-preparation.yml`.
  This records owner authorization to prepare, not a contract freeze,
  independent review, clinical validation or Track 008 completion.
- [x] Generate 9,758 provisional exact-release ORPHA-to-MONDO mapping rows,
  preserve 9,758 paired source labels and 20,413 HPO source-native labels,
  exclude 27 MONDO assertions absent from the exact Orphadata release, and
  re-run the bounded challenge. Evidence:
  `manifests/semantics/track-008-v0.4-orpha-mondo-mappings.json`,
  `manifests/semantics/track-008-v0.4-provisional-naming.json`,
  `manifests/semantics/track-008-v0.4-row-generation-receipt.json` and
  `docs/track-008-v0.4-candidate-challenge-2026-08-21.yml`. Rows remain
  provisional, moderate-confidence and non-clinical; no new groupings were
  created.
- [ ] Present the final exact hashes, migration impact and bounded challenge
  for owner disposition; do not freeze or complete Track 008 automatically.

## Review fixes — 2026-08-21

- [x] Resolve full-gate lint findings in the candidate-binding validator,
  HPO provenance renderer and negative hash-drift test without changing any
  semantic candidate or gate state. Evidence: focused Track 008 tests and the
  full repository validation gate.
