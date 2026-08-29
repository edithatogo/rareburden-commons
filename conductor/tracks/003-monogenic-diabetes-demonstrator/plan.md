# Track 003 plan

> Repository-owned review uses the subagent panel under ADR-0009; external clinical and patient/community authority remains a separate gate.

## Phase 1 — Protocol and definitions

- [x] Register bounded RBC-P002 v0.2.0 with explicit estimands and denominator options. Evidence: `docs/track-003-rbc-p002-bounded-registration-2026-08-29.yml` and `scripts/check_track003_bounded_registration.py`; execution remains disabled. `[M-01, M-03, S-05]`
- [x] Bind the synthetic monogenic-diabetes entity scope and hierarchy version while explicitly leaving clinical gene/phenotype scope unfrozen. Evidence: the bounded registration and `docs/decisions/2026-08-29-track-003-bounded-interface-scope.yml`. `[M-02, S-01]`
- [x] Bind the diagnosed, undiagnosed, modelled, unclassified and out-of-scope population-state contract. Evidence: bounded registration plus `docs/track-003-population-state-contract-v0.1.0.yml`. `[M-04]`
- [x] Obtain clinical-methods and community/harm agent-panel review of framing and owner disposition. Evidence: `docs/reviews/track-003-bounded-scientific-agent-2026-08-29.yml`, `docs/reviews/track-003-bounded-simulated-community-harm-agent-2026-08-29.yml` and `docs/decisions/2026-08-29-track-003-bounded-registration-disposition.yml`; these are advisory repository evidence, not independent, clinical or community authority.

## Phase 2 — Evidence ledger

- [ ] Extract and assess aetiologic-fraction evidence by age, phenotype, ancestry and setting. `[M-21]`
- [ ] Ledger diagnosis delay, treatment change, complications and service-use evidence. `[M-04, M-11]`
- [ ] Define transportability and referral-bias sensitivity parameters. `[S-07]`
- [ ] Record unresolved evidence gaps and data-access asks. `[M-26]`

## Phase 3 — Analysis implementation

- [x] Build a non-binding public/synthetic analysis specification and fixture. Evidence: `examples/analyses/monogenic-diabetes-synthetic.yml` and schema-validation test; empirical activation and contract freeze remain blocked. `[M-18, M-19]`
- [ ] Run primary expected-population and rare-aetiology models. `[S-04, S-05]`
- [ ] Add structural, denominator, ascertainment and penetrance scenarios. `[M-06]`
- [ ] Add outcome/economic scenarios only where compatible evidence exists. `[S-06]`

## Phase 4 — Validation and reporting

- [ ] Compare with independent cohort or registry evidence where lawful. `[S-10]`
- [ ] Complete numerical, scientific and language agent-panel review and owner disposition.
- [ ] Produce reproducible report, data package and limitations summary.
- [ ] Record review findings and approve, narrow, revise or stop.

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

- [x] Pin the exact upstream commit/tree rather than accepting an arbitrary resolvable pair.
- [x] Validate every registered estimand, denominator, entity, population-state dimension and derived quantity against its bound contract, with mutation coverage.
- [x] Add a current bounded framing overlay that preserves false empirical, controlled-data, independent-review and community-authority claims while retaining the historical guard unchanged.
- [x] Re-run the role-separated panel against corrected exact candidate `675c38e`; all three lanes passed with no unresolved blocker, and the owner accepted the bounded registration without authorizing execution or completing Track 003.
