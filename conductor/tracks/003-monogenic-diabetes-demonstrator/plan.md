# Track 003 plan

> Repository-owned review uses the subagent panel under ADR-0008; external clinical and patient/community authority remains a separate gate.

## Phase 1 — Protocol and definitions

- [ ] Register RBC-P002 with explicit estimands and denominator options. `[M-01, M-03, S-05]`
- [ ] Freeze monogenic-diabetes entities, gene/phenotype scope and ontology versions. `[M-02, S-01]`
- [ ] Define diagnosed, undiagnosed and modelled population states. `[M-04]`
- [ ] Obtain clinical-methods and community/harm agent-panel review of framing and owner disposition.

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
