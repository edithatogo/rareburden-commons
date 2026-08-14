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
