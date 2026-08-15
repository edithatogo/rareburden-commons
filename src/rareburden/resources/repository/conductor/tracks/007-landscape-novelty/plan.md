# Track 007 plan

> Repository-owned review uses the subagent panel under ADR-0008; independent methods and patient/community challenge remain separate release gates.

## Phase 1 — Register the review

- [x] Define provisional questions, inclusion logic, sources and extraction fields.
- [ ] Register the landscape-review protocol externally and version the complete search strategy.
- [x] Define initiative, dataset, software, standard, mandate and methodological-precedent fields.
- [ ] Recruit patient/community and independent methods reviewers.

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
- [ ] Obtain external methodological and patient/community challenge and revise claims.
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
- [ ] Obtain protocol registration, independent methods challenge and
  patient/community interpretation; until then retain provisional landscape
  claims and `in_review` status.

## Registration/challenge readiness refresh — 2026-08-04

- [x] Prepare a single versioned readiness packet binding the registration
  snapshot, methods challenge questions, patient/community interpretation
  questions, receipt fields and stop triggers. Evidence:
  `docs/track-007-registration-challenge-readiness-2026-08-04.yml` and
  `tests/test_track_007_readiness.py`.
- [ ] Submit the frozen protocol and record an external registry identifier;
  the readiness packet is not registration evidence.
- [ ] Obtain an independent methods challenge and accountable
  patient/community interpretation; repository tests and panels cannot replace
  either receipt.

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
- [ ] Obtain protocol registration, independent methods challenge and
  patient/community decision after panel preparation; panels cannot close
  these gates.
