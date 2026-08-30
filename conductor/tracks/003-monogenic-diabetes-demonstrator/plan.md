# Track 003 plan

> Repository-owned review uses the subagent panel under ADR-0009; external clinical and patient/community authority remains a separate gate.

Current acceptance and evidence: [synthetic reference closeout](../../../docs/track-003-reference-closeout-2026-08-31.md). The dated preparation sections below preserve historical status; the current four phases are adjudicated by the exact Option A execution, reproduction and output review. Hosted checks remain a merge gate.

## Phase 1 — Protocol and definitions

- [x] Register bounded RBC-P002 with explicit estimands and denominator options. Evidence: `docs/track-003-rbc-p002-bounded-registration-2026-08-29.yml` and the approved reference candidate. [M-01, M-03, S-05]
- [x] Bind synthetic entity scope and versioned D/E/G definitions; clinical gene/phenotype scope remains unfrozen. Evidence: bounded registration and manifest-bound reference inputs. [M-02, S-01]
- [x] Bind diagnosed, undiagnosed, modelled, unclassified and out-of-scope state distinctions. Evidence: population-state contract and actual report/CSV/JSON. [M-04]
- [x] Obtain scientific and simulated harm framing challenge and owner disposition. Evidence: original bounded reviews, output panel and explicit recorded Option A; no independent/clinical/community authority.

## Phase 2 — Evidence ledger

- [x] Extract and assess aetiologic-fraction evidence by age, phenotype, ancestry and setting. Evidence: `docs/track-003-aetiologic-evidence-qualification-2026-08-30.yml`; candidates remain sensitivity-only or unsuitable, not executed empirical inputs. [M-21]
- [x] Ledger diagnosis delay, treatment change, complications and service-use evidence. Evidence: outcome/service ledger, source-qualification addendum, licensed pathway ledger and gap register. Closeout explicitly accepts descriptive records and held/gap family dispositions, not nonexistent empirical rates. [M-04, M-11]
- [x] Define transportability and referral-bias sensitivity parameters. Evidence: transport contract, eighteen assumed input records and twelve executed scenarios. These are invented hypothetical parameters, not calibrated empirical ranges. [S-07]
- [x] Record unresolved evidence gaps and access asks. Evidence: `docs/track-003-evidence-gap-register-2026-08-30.yml`; asks remain unsent and source-specific gaps open. [M-26]

## Phase 3 — Analysis implementation

- [x] Build public/synthetic analysis specification and reference dataset. Evidence: `examples/demonstrators/track-003-reference-inputs.json`, schemas, tests and exact candidate manifest. [M-18, M-19]
- [x] Run primary expected-population and rare-aetiology models. Evidence: `manifests/demonstrators/track-003-reference-execution-2026-08-31.json` and the three-file results package. [S-04, S-05]
- [x] Run structural, denominator, ascertainment and penetrance scenarios, with age, calendar, ancestry-applicability and referral assumptions explicit. Twelve seeded scenarios and deterministic plug-ins reproduced exactly. [M-06]
- [x] Add compatible, explicitly hypothetical outcome/economic scenarios. Full-year eligibility, fictional currency, conditional delay and non-causal treatment change are labelled; no empirical outcome model inferred. [S-06]

## Phase 4 — Validation and reporting

- [x] Compare with independent cohort or registry evidence where lawful. The closeout explicitly adjudicates the bound source applicability/noncomparability assessment: incompatible selected populations/endpoints cannot validate fictional quantities. This is not empirical agreement testing. [S-10]
- [x] Complete numerical, scientific and language agent-panel review and apply explicit Option A conditions. Evidence: `docs/reviews/track-003-reference-output-panel-2026-08-31.yml` and exact decision.
- [x] Produce reproducible report, data package and limitations summary. Evidence: `results/track-003-reference-2026-08-31/`, exact two-run receipts, source/environment manifest and closeout instructions.
- [x] Record findings and conditional approve/revise/stop disposition. All output lanes pass; eight original criteria are mapped in the closeout. Offline retained-evidence validation does not execute analysis. Local and hosted checks must pass before merge.

## Dependency review — 2026-07-27

- [x] Record that Track 003 cannot activate until Tracks 008, 009 and 010 are complete. Evidence: `0cd41f3`.
- [x] Add non-binding RBC-P002 v0.1.0 protocol draft to the specification; activation and contract freeze remain blocked.

## Preparation refresh — 2026-08-01

- [x] Prepare the RBC-P002 review packet with entity, denominator, state,
  transportability, outcome and framing decisions. Evidence:
  `docs/track-003-rbc-p002-review-packet.md`; dependencies and external clinical,
  methods, governance and patient/community review remain open.
- [x] Prepare the non-binding RBC-P002 protocol draft with explicit estimand
  and denominator decision fields; registration and freeze remain open.

## Synthetic estimand and denominator preparation — 2026-08-20

- [x] Define a non-binding, machine-tested estimand and denominator contract
  that separates compatible diabetes denominators, diagnosed-only sensitivity,
  referral-cohort bias diagnostics and total-population chain estimands.
  Evidence: `docs/track-003-estimand-denominator-contract-v0.1.0.yml` and
  `tests/test_track_003_estimand_denominator_contract.py`. The existing
  mathematical engine fixture remains assurance-only and is explicitly not an
  RBC-P002-compatible analysis. Registration, empirical activation and all
  upstream, clinical, community and governance gates remain open.
- [x] Define non-binding population-state semantics that keep observed
  diagnosis, latent model states, unclassified records and referral/testing
  selection distinct, with aligned-partition and double-counting guards.
  Evidence: `docs/track-003-population-state-contract-v0.1.0.yml` and
  `tests/test_track_003_population_state_contract.py`. Undiagnosed burden
  remains a modelled scenario quantity, never an observed count; activation
  and all upstream and external gates remain open.

## Synthetic framing and interpretation preparation — 2026-08-21

- [x] Define a machine-tested, non-binding framing and interpretation guard
  requiring evidence-status labels, denominator and uncertainty visibility,
  explicit selection/overlap limits, harm/equity challenges and fail-closed
  prohibited uses. Evidence:
  `docs/track-003-framing-interpretation-guard-v0.1.0.yml` and
  `tests/test_track_003_framing_interpretation_guard.py`. Clinical-methods,
  patient/community and owner dispositions remain pending; this repository
  preparation is not independent review, consent, endorsement or activation.

## Synthetic evidence-extraction preparation — 2026-08-21

- [x] Define a machine-tested, empty aetiologic-fraction evidence-extraction
  contract with source/version/rights provenance, aligned numerator and
  denominator fields, age/phenotype/ancestry/setting/ascertainment strata,
  non-composite quality domains, conflict/overlap/missingness rules and
  accountable verification states. Evidence:
  `docs/track-003-aetiologic-fraction-evidence-contract-v0.1.0.yml` and
  `tests/test_track_003_aetiologic_fraction_evidence_contract.py`. No source
  search, empirical extraction, verification, synthesis or parameter creation
  has occurred; the Phase 2 empirical evidence task and all upstream and
  external gates remain open.

## Synthetic outcome and service-ledger preparation — 2026-08-21

- [x] Define a machine-tested, empty evidence-ledger contract for diagnosis
  delay, treatment change, complications and service use, keeping reported
  results, transformations, modelled scenarios and assumptions distinct.
  Evidence:
  `docs/track-003-outcome-service-evidence-ledger-contract-v0.1.0.yml` and
  `tests/test_track_003_outcome_service_evidence_ledger_contract.py`. The
  contract rejects causal treatment claims, incompatible outcome measures,
  case-fraction allocation of complications or utilisation, event/person
  confusion and silent overlap or missingness handling. No source search,
  extraction, empirical comparison, synthesis or parameter creation occurred;
  the Phase 2 empirical ledger task and all upstream and external gates remain
  open.
> Review routing (owner direction, 2026-08-22): clinical/scientific, patient/community and data-governance/custodian questions are sent to role-separated advisory agents and presented to the repository owner for disposition. Security/engineering approval is an explicit owner-operated decision lane. Agent advice and owner-operated evidence do not create independent, community or custodian approval.

## Bounded interface activation — 2026-08-29

- [x] Reconcile completed Tracks 008–010 and advance the internal roadmap to v0.5.0 without claiming package publication or production release. Evidence: `docs/decisions/2026-08-29-bounded-v0.5-roadmap-progression.yml` and `a00078a`.
- [x] Add a fail-closed RBC-P002 bounded registration with exact upstream, semantic, ledger, burden-engine, estimand, population-state and framing hashes plus mutation tests for every prohibited claim. Evidence: `docs/track-003-rbc-p002-bounded-registration-2026-08-29.yml` and `tests/test_track003_bounded_registration.py`.
- [x] Complete exact-candidate scientific/methods, engineering and simulated community/harm agent review and record the repository-owner disposition. Evidence: `docs/reviews/track-003-bounded-*-agent-2026-08-29.yml` and `docs/decisions/2026-08-29-track-003-bounded-registration-disposition.yml`.
- [x] Qualify a protocol-compatible synthetic denominator before any RBC-P002 run, complete exact scientific, engineering and simulated-harm review, record owner disposition and retain exactly one provenance-bound synthetic assurance output. Evidence: `docs/track-003-rbc-p002-synthetic-denominator-candidate-2026-08-29.yml`, `docs/reviews/track-003-synthetic-denominator-*-2026-08-29.yml`, `docs/decisions/2026-08-29-track-003-synthetic-denominator-disposition.yml` and `manifests/demonstrators/track-003-rbc-p002-synthetic-execution-closeout-2026-08-29.yml`. Empirical, controlled-data, public-aggregate, clinical, independent-review, community, publication and production-release claims remain false.

### Review fixes

- [x] Update roadmap snapshot counts for Track 003 completion and explicitly mark a copied test fixture incomplete, preserving released-release rejection without relying on unfinished live project work. Evidence: `tests/test_roadmap.py`.

- [x] Add the non-executing retained-evidence validator and twelve mutation checks; restore declared metric order when rendering sorted JSON summaries. Correct full-checkout result/receipt references in installed documentation without changing approved outputs. Evidence: current closeout and rebound output-panel receipt.

- [x] Address PR #275 hosted runtime and atomic-publication findings. Actual Python 3.13 and locked dependencies are checked before execution/retention; staged outputs are flushed and renamed together. Evidence: `docs/reviews/track-003-reference-package-hosted-fixes-2026-08-30.yml`; 27 focused tests pass. Exact owner decision remains pending.

- [x] Challenge the exact-package implementation across scientific, engineering and simulated-harm lanes; fix execution-root binding, decision-byte/drift verification, strict decision validation and self-contained uncertainty/definition reporting. Evidence: `docs/reviews/track-003-reference-package-panel-2026-08-30.yml`; 18 focused tests pass. No governed reference output has been retained.

- [x] Challenge the twelve-scenario runner; distinguish assumed conditional inputs at empty conditioning sets, add metric metadata and scenario parameter bindings, and test approximate denominator partitions and invalid numerical inputs. Evidence: `docs/reviews/track-003-reference-runner-panel-2026-08-30.yml`; 62 focused tests pass. Full candidate disposition and retained results remain pending.

- [x] Audit original reference-analysis acceptance through three advisory lanes and remove the inferred need for a synthetic-first scope reduction. Evidence: `docs/track-003-full-reference-acceptance-2026-08-30.md`. All original deliverables remain required; input preparation is not execution or completion. Additional source qualification is recorded in `docs/track-003-additional-source-screen-2026-08-30.md` without promoting either source to model input.
- [x] Challenge synthetic scenario arithmetic with three advisory lanes; fix huge-integer overflow rejection and add five regression cases. Evidence: `docs/reviews/track-003-synthetic-scenario-panel-2026-08-30.yml`; 73 focused tests pass. This does not complete scenario execution or empirical qualification.
- [x] Pin the exact upstream commit/tree rather than accepting an arbitrary resolvable pair.
- [x] Validate every registered estimand, denominator, entity, population-state dimension and derived quantity against its bound contract, with mutation coverage.
- [x] Add a current bounded framing overlay that preserves false empirical, controlled-data, independent-review and community-authority claims while retaining the historical guard unchanged.
- [x] Re-run the role-separated panel against corrected exact candidate `675c38e`; all three lanes passed with no unresolved blocker, and the owner accepted the bounded registration without authorizing execution or completing Track 003.
