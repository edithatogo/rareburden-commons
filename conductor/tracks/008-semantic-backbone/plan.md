# Track 008 plan

> Repository-owned review uses the subagent panel under ADR-0008; clinical and patient/community semantic authority remains separate.

## Phase 1 — Contracts and source releases

- [x] Define disease-definition and mapping schemas. `[M-01, M-02, M-18]`
  Evidence: ontology-mapping and hierarchy schemas with strict semantic tests;
  source release approval remains open.
- [x] Pin the exact bounded ontology releases and licence states used by the
  provisional semantic core. Broader source classes remain an explicit
  expansion gate in `docs/decisions/2026-08-22-track-008-bounded-completion.yml`.
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
- [x] Run the clinical-methods and simulated community/harm naming challenge
  through role-separated agents and record the repository-owner disposition.
  Evidence: `docs/track-008-v0.4-candidate-challenge-2026-08-21.yml` and
  `docs/decisions/2026-08-21-track-008-v0.4-final-disposition.yml`. This is an
  owner-operated simulation, not clinical validation, lived-experience
  participation or authority for any unrelated community.

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

- [x] Run role-separated semantic/methods agent-panel review and owner
  disposition. Evidence: `docs/track-008-bounded-agent-review-2026-08-16.yml`,
  `docs/track-008-v0.4-candidate-challenge-2026-08-21.yml` and the exact
  Option A owner disposition. The agent panel is advisory and not independent
  human review.
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
- [x] Freeze the exact bounded provisional non-clinical v0.4 semantic contract
  for dependency integration. Evidence: the hash-bound Option A disposition
  and satisfied scoped freeze gate. This is not Track 008 completion or
  authority to activate excluded sources, clinical use or public naming.

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
- [x] Obtain the simulated clinical/community agent-panel naming recommendation
  and owner disposition for the bounded candidate. This closes the repository
  governance task only; clinical validity and actual-community participation,
  consent, endorsement and authority remain unclaimed.
- [x] Pin the approved bounded source releases and exact public asset allowlist.
  Evidence: the v0.4 candidate manifest binds Orphadata, MONDO and nine cleared
  HPO ontology-core objects; all other source classes remain excluded.
- [x] Freeze the bounded v0.4 semantic contract after upstream Track 002/007
  reconciliation and resolution of findings within the narrowed non-clinical
  scope. Expansion findings remain open and fail closed.
- [x] Record the source- and rights-holder evidence boundary for the exact
  bounded allowlist. Expansion or redistribution of excluded source classes is
  deferred outside this bounded completion and remains fail-closed.

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
- [x] Reconcile the completed Track 002/007 outcomes with the bounded source
  and naming challenge and record the owner disposition. The resulting scope
  is complete only for the provisional non-clinical core; broader authority
  remains pending outside this track.

## Bounded completion scope — 2026-08-22

- [x] Record the selective completion decision, exact allowlist, prohibited
  claims and expansion gates in
  `docs/decisions/2026-08-22-track-008-bounded-completion.yml`.
- [x] Preserve Track 009 as blocked on its own evidence, governance and v0.4
  freeze gates; only the bounded semantic dependency is satisfied.

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
  v0.4 freeze and Track 009 activation remain blocked.

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
  This records the historical preparation decision; the later bounded
  completion decision is authoritative for the exact non-clinical scope.
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
- [x] Prepare and present the final exact hashes, migration impact, bounded
  challenge and two fallback options for owner disposition. Evidence:
  `docs/decisions/2026-08-21-track-008-v0.4-final-disposition.yml` and the
  subsequent owner decision in
  `docs/decisions/2026-08-22-track-008-bounded-completion.yml`.
- [x] Record the owner's exact-candidate Option A disposition for commit
  `47f1a9159e85bfa8112c18ca1c1c69b29e99b4cd` and tree
  `af2bc0074ae6c77a65f8c47da04431b08baca77f`, and apply only the bounded
  provisional non-clinical contract freeze. Track 008 is complete for this
  bounded scope; source-rights expansion, clinical validity and actual-community
  naming-authority gates remain conditional expansion gates. Independent human
  review is not a gate in this single-person repository; agent panels advise and
  the owner decides.

## Review fixes — 2026-08-21

- [x] Resolve full-gate lint findings in the candidate-binding validator,
  HPO provenance renderer and negative hash-drift test without changing any
  semantic candidate or gate state. Evidence: focused Track 008 tests and the
  full repository validation gate.

## Exact ICD metadata preparation — 2026-08-21

- [x] Bind the already-observed WHO ICD-11 MMS `2026-01` English API v2
  release-metadata response to an exact endpoint, date, size and SHA-256 while
  retaining private response bytes, unresolved terms, unassessed mapping
  fitness and disabled activation. Evidence:
  `docs/track-008-icd11-mms-2026-01-metadata-packet.yml` and
  `tests/test_track008_icd11_metadata_packet.py`. This does not complete the
  parent source-pinning task, validate a mapping, authorize redistribution or
  change the bounded provisional v0.4 semantic candidate.

## Bounded completion reconciliation — 2026-08-22

- [x] Record completion of the exact provisional non-clinical semantic core
  after the Track 002/007 dependency outcomes, with role-separated agent
  advice and owner disposition. Evidence:
  `docs/decisions/2026-08-22-track-008-bounded-completion.yml`.
- [x] Preserve source-rights, mapping-fitness, clinical-validity,
  community-authority and production-release conditions as explicit expansion
  gates. No additional or independent human review is required for the
  bounded repository scope.
