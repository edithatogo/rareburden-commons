# Track 007 plan

> Review uses role-separated agent panels and repository-owner disposition under ADR-0009; no additional-person or independent review gate applies.

## Phase 1 — Register the review

- [x] Define provisional questions, inclusion logic, sources and extraction fields.
- [x] Freeze and hash-register the protocol and complete search strategy in the
  repository; external registry submission is optional. Evidence:
  `docs/track-007-protocol-v0.2.0.md` and
  `docs/track-007-repository-registration-2026-08-16.yml` bind the protocol and
  evidence by SHA-256 and Git blob identifier; OSF is deferred and removed from
  the active plan.
- [x] Define initiative, dataset, software, standard, mandate and methodological-precedent fields.
- [x] Obtain role-separated methods/coverage, community/harm,
  governance/rights/reproducibility and scientific/search-reproducibility agent
  findings bound to the repository registration. Evidence:
  `docs/track-007-agent-panel-findings-2026-08-16.yml`. The advisory consensus
  is `narrow_and_remediate`; agent advice is not independent, human or
  constituted-community approval.

## Phase 2 — Search and screen

- [x] Complete an initial search of cited scholarly and institutional infrastructures.
- [x] Run repository-native GitHub, Zenodo and Hugging Face searches reproducibly. Evidence: dated API metadata recorded in review, 2026-07-27; historical OSF observations are retained only in the review archive.
- [x] Seed registry, genomic, burden, policy and standards ecosystems in the landscape register.
- [x] Complete seed-catalogue deduplication, screening and an auditable exclusions log. Evidence: `docs/landscape-screening-007.md` (`RBC-LAND-007-SCREEN v0.1.0`), 2026-07-29; broader discovery screening remains explicitly open.
- [x] Preserve and screen every result on the bounded v0.2.0 public-API first
  pages, reconcile exact cross-query/DOI duplicates, exclude the repository's
  self-result and flag rather than over-merge exact-title entity candidates.
  Evidence: `docs/track-007-search-results-2026-08-15.json`,
  `docs/track-007-screening-2026-08-15.json`,
  `scripts/screen_track_007_results.py` and `tests/test_landscape.py`; pagination,
  full-text eligibility, coverage, novelty and external challenge remain open.
- [x] Resolve the bounded first-page screen's sole uncertain record through its
  Crossref persistent identifier, preserve the response hash and observed
  metadata, and keep broader coverage claims disabled. Evidence:
  `docs/track-007-screening-resolutions-2026-08-15.json`; bounded counts are 69
  included for full-text review, 51 excluded and 0 uncertain.
- [x] Implement and exercise a deterministic, fail-closed full-text eligibility
  workflow for all 69 retained records without retaining abstracts or
  copyrighted full text. Evidence:
  `scripts/observe_track_007_locators.py`,
  `scripts/assess_track_007_fulltext.py`,
  `docs/track-007-fulltext-locator-observations-2026-08-15.json`,
  `docs/track-007-fulltext-eligibility-2026-08-15.json`, schema and negative
  tests. The bounded HEAD-only observation found 61 reachable and 8 restricted
  locators; all remain pending content assessment or lawful access. Final
  eligibility, novelty, completeness and external challenge remain
  open.
- [x] Add a deterministic, fail-closed pagination strategy and executable
  bounded capture workflow for GitHub, Zenodo and Hugging Face public endpoints.
  Evidence: `scripts/capture_track_007_pages.py`,
  `docs/track-007-pagination-strategy-2026-08-15.json`,
  `docs/track-007-pagination-workflow.md` and
  `tests/test_track_007_pagination.py`; no live multi-page capture or ecosystem
  completeness claim is inferred.
- [x] Execute the bounded live pagination workflow across the five frozen queries
  for GitHub, Zenodo and Hugging Face, preserving exact request/final URLs,
  retrieval windows, response hashes, provider totals and stop reasons. Evidence:
  `docs/track-007-live-capture-coverage-2026-08-15.json` and its three bound
  provider capture files. GitHub endpoint totals were reached, Zenodo remained
  page-budget limited, and empty Hugging Face results were not interpreted as
  absence or completeness. Screening of newly captured records remains open.
- [x] Record a fail-closed coverage and representativeness disposition for the
  live capture. Global representativeness, comprehensive coverage and upgraded
  novelty remain prohibited; language, geography, grey-literature and restricted
  material coverage remain unmeasured or incomplete.
- [x] Adjudicate all four exact-title clusters at record level using hash-bound
  GitHub and Crossref observations. Evidence:
  `docs/track-007-title-cluster-adjudication-2026-08-15.json`. The reciprocal
  preprint/article relation is linked as one work while preserving both records;
  three GitHub pairs remain separate repository records with initiative-level
  equivalence explicitly unresolved.

## Substantive evidence continuation — 2026-08-16

- [x] Reconcile all 306 bounded live-capture occurrences by exact provider
  identifier. Evidence: `docs/track-007-live-reconciliation-2026-08-16.json`
  records 215 unique identifiers, 91 exact duplicate occurrences, 71 exact
  frozen-snapshot matches and 144 live-only identifiers.
- [x] Observe every live-only identifier through its current public record
  endpoint with rate limiting, retaining response hashes and minimal metadata
  but no descriptions, abstracts, bodies or full text. Evidence:
  `docs/track-007-live-metadata-observations-2026-08-16.json` records 51
  candidates for content assessment and 93 uncertain metadata signals; none is
  excluded.
- [x] Apply the closed-vocabulary public-description rule to the frozen 69
  records. Evidence: `docs/track-007-public-metadata-resolutions-2026-08-16.json`
  and `docs/track-007-fulltext-eligibility-2026-08-16.json` record 35 bounded
  metadata-supported includes, 26 pending content assessments and 8 pending
  lawful-access cases, with zero new exclusions.
- [x] Observe the remaining 26 reachable frozen records through lawful public
  Crossref or GitHub metadata and apply the exact closed-vocabulary rule.
  Evidence: `docs/track-007-pending-public-content-2026-08-16.json` and the
  combined v0.3.0 eligibility register record 21 additional includes, 2 explicit
  duplicate/non-substantive-release exclusions, 1 uncertain record and 2
  pending public-evidence records.
- [x] Resolve the remaining 2 public-evidence-pending and 1 uncertain frozen
  records through exact Zenodo/GitHub public metadata. Evidence:
  `docs/track-007-fulltext-eligibility-v0.3.1-2026-08-16.json` records 59
  includes, 2 exclusions and only the 8 lawful-access cases pending.
- [ ] Resolve the 8 restricted frozen records through a lawful access route or
  an adequate public alternative; restriction is never exclusion evidence.
- [x] Screen all 144 live-only records with the exact scope/contribution
  vocabulary and response hashes. The result is 51 content-assessment
  candidates and 93 uncertain records, with zero exclusions.
- [ ] Complete final content assessment for the 51 live-only candidates and
  resolve the 93 uncertain records without inferring exclusion, absence,
  coverage or novelty from missing evidence.
- [x] Record bounded adjacency eligibility for the 51 live-only records with
  both exact public scope and contribution signals; retain all 93 other records
  as uncertain, never excluded. Evidence:
  `docs/track-007-live-final-eligibility-2026-08-16.json`.
- [x] Execute a strict two-page, 20-row Crossref expansion for the five frozen
  queries plus four multilingual and three community/community-multilingual
  queries. Evidence: `docs/track-007-bibliographic-expansion-2026-08-16.json`
  records 24 rate-limited requests and 480 ranked DOI occurrences, with record
  language missing for all observations and geography explicitly unmeasured.

## Review fixes — 2026-08-15 title clusters

- [x] Distinguish hashes of temporary `gh api` observation bytes from hashes of
  direct Crossref response bytes and state that raw payloads were not retained,
  preventing the adjudication packet from implying a raw-response archive.

## Review fixes — 2026-08-15 live capture

- [x] Make dated capture creation atomic and fail closed with exclusive file
  creation, preventing a concurrent writer from bypassing the no-overwrite
  evidence contract. Evidence: CLI overwrite regression test in
  `tests/test_track_007_pagination.py`.

## Phase 3 — Analyse adjacency

- [x] Compare scope, geography, disease coverage, access, methods, outputs and maturity.
- [x] Identify foundational dependencies, candidate partners and conflicting mandates.
- [x] Test the programme thesis against the initial adjacency evidence.
- [x] Produce a machine-readable adjacency and white-space map.

## Phase 4 — Decide and publish

- [x] Draft the adjacency matrix and provisional landscape report.
- [x] Record the repository-owner `accept`, `narrow`, `revise`, `defer` or
  `stop` disposition against the exact panel input and findings, including
  claim revisions, unresolved findings and stop triggers. Evidence:
  `docs/track-007-owner-disposition-ready-2026-08-16.yml` records Option A
  `narrow` against merged candidate commit `1f93f5862290e16d0e393834e35c282d187658e1`
  and tree `97bb9387053f4e8feb30d2310fbc849e5ecbb8da`, while preserving the original
  publication-ready acceptance as unmet. The attributable owner receipt is
  GitHub issue comment `5303053641`.
- [x] Record the provisional `proceed_with_narrowed_scope` decision.
- [x] Update the roadmap and programme framing to avoid duplicating registries, ontologies or genomic platforms.

## Review fixes — 2026-07-27

- [x] Reconcile the internal review with the current 13-item catalogue and keep provisional and external gates distinct. Evidence: `a18cee0`.
- [x] Run and record bounded GitHub, Zenodo and Hugging Face repository-native discovery searches with dated API metadata. Evidence: review record updated 2026-07-27; screening, deduplication, registration and external challenge remain open.
- [x] Run a mechanical duplicate check over the current 13-item catalogue (unique IDs and official URLs). Evidence: review record updated 2026-07-27; semantic screening and exclusions remain open.
- [x] Produce versioned draft search strings, eligibility rules, screening workflow and exclusions fields for external registration. Evidence: `RBC-LAND-007 v0.1.0` in review record, 2026-07-27; registration and independent review remain open.
- [x] Record a preliminary 13-record seed-catalogue screening baseline with counts and explicit zero-exclusion caveat. Evidence: review record updated 2026-07-27; final screening and exclusions remain open.
- [x] Record the historical registry-route observations without treating them as current registration work. The active registration route is now registry-neutral with Zenodo as the prepared fallback.

## Preparation refresh — 2026-08-01

- [x] Add the registration handoff, search-log schema, screening/exclusion
  fields and count-reconciliation rules. Evidence:
  `docs/track-007-registration-packet.md`; external registration and independent
  review remain open.
- [x] Preserve the bounded 2026-08-01 discovery observations as a structured
  search log. Evidence: `docs/track-007-search-log-2026-08-01.yml`; screening,
  registration and independent review remain open.
- [x] Refresh all five registered query families across GitHub, Zenodo,
  Hugging Face datasets and Crossref with exact timestamps, result observations,
  response hashes and bounded identifiers. Evidence:
  `scripts/refresh_track_007_searches.py` and
  `docs/track-007-search-log-2026-08-14.yml`; OSF remains deferred and all new
  records remain unscreened.
- [x] Bind the refreshed protocol, search log and screening register into a
  versioned methods and patient/community challenge-readiness packet. Evidence:
  `docs/track-007-registration-challenge-readiness-2026-08-15.yml`; receipts
  remain pending and the packet records low-specificity, representativeness,
  deduplication and self-result challenges explicitly.
- [x] Add a regression guard for the versioned search-log schema and its
  discovery-only/provisional boundary in `tests/test_landscape.py`.

## Synthetic screening exercise — 2026-08-02

- [x] Exercise count reconciliation, exclusion reasons and unresolved-record
  handling with a deterministic fixture. Evidence:
  `docs/track-007-panel-screening-exercise-2026-08-02.yml` and
  `tests/test_landscape.py`; this is panel preparation only and does not close
  registration or independent challenge gates.

## Closure plan — 2026-08-02

- [x] Add the dependency-ordered closure plan shared with Track 002 in
  `docs/track-002-007-closure-plan-2026-08-02.md`.
- [x] Consolidate the duplicated closure wording into the canonical Phase 1
  agent-challenge task and Phase 4 owner-disposition task. Repository
  hash-registration is complete; until the two canonical tasks close, retain
  provisional landscape claims and `in_review` status.

## Pagination screening-metadata contract — 2026-08-15

- [x] Retain stable identifiers, titles and canonical URLs alongside each
  hash-addressed captured page so a later dated capture can enter deterministic
  screening without retaining abstracts, bodies or full text. Malformed and
  overlong metadata fail closed. Evidence:
  `scripts/capture_track_007_pages.py`,
  `tests/test_track_007_pagination.py`, and
  `docs/track-007-pagination-workflow.md`. Existing captures are not rewritten;
  this contract applies to subsequent immutable captures.

## Registration/challenge readiness refresh — 2026-08-04

- [x] Prepare a single versioned readiness packet binding the registration
  snapshot, methods challenge questions, patient/community interpretation
  questions, receipt fields and stop triggers. Evidence:
  `docs/track-007-registration-challenge-readiness-2026-08-04.yml` and
  `tests/test_track_007_readiness.py`.
- [x] Record the frozen protocol hash and immutable repository locator; an
  external registry identifier is optional supplementary evidence. Evidence:
  `docs/track-007-repository-registration-2026-08-16.yml`.
- [x] Route challenge and disposition through the canonical Phase 1 and Phase 4
  tasks instead of maintaining a second checklist gate.

## Panel closure planning — 2026-08-02

- [x] Add the joint Track 002/007 panel closure plan with options,
  contingencies and dependency sequence in
  `docs/track-002-007-panel-closure-plan-2026-08-02.md`.
- [x] Record the approved staged registration, independent methods challenge
  and patient/community interpretation plan with bounded fallbacks. Evidence:
  `docs/track-007-staged-registration-challenge-plan-2026-08-03.yml` and
  `tests/test_track_007_staged_plan.py`; external gates remain pending.
- [x] Prepare a schema-valid synthetic Track 007 panel packet with pending
  registration and challenge receipts in `examples/fixtures/track-007-panel-packet-synthetic.json`.
- [x] Route repository registration, agent challenge and owner disposition
  through the canonical Phase 1 and Phase 4 tasks; do not duplicate their
  lifecycle state in this historical planning section.
