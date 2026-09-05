# Track 011 plan

> Repository-owned review uses the subagent panel under ADR-0008; respiratory clinical and patient/community review remains separate.

## Phase 1 — Protocol and semantic scope

- [x] Define and bound bronchiectasis denominator populations for synthetic assurance. Evidence: `examples/demonstrators/011-bounded-synthetic-profile.yml`.
- [x] Define included rare aetiologies and ontology versions for the non-binding semantic fixture. Evidence: `examples/semantics/bronchiectasis-synthetic.yml`. `[M-01, M-02]`
- [x] Define multi-aetiology, unclassified and overlapping categories. Evidence: `manifests/demonstrators/track-011-bounded-synthetic-receipt-2026-08-16.json`. `[M-05]`
- [x] Complete repository-owned agent-panel preparation packet; clinical and community authority remain external gates. Evidence: `docs/track-011-rbc-p003-review-packet.md`.

## Phase 2 — Evidence and transportability

- [x] Extract and qualify aetiologic-fraction evidence by age, setting and diagnostic capacity. Evidence: `docs/track-011-aetiologic-evidence-qualification-2026-09-05.yml` qualifies EMBARC, Australian Registry and guideline literature as sensitivity-only; empirical parameter creation remains excluded. `[M-21]`
- [x] Ledger outcomes, delay and service use with quality grades. `[M-21]` Evidence: `docs/track-011-outcome-service-evidence-ledger-2026-09-05.yml` and `docs/track-011-evidence-gap-register-2026-09-05.yml`; closeout explicitly accepts descriptive scenario models and held/gap dispositions, not nonexistent empirical rates.
- [x] Model referral, testing and case-definition bias in the bounded analysis specification. Evidence: `examples/analyses/bronchiectasis-synthetic.yml`.
- [x] Specify geography and health-system transfer scenarios without extrapolation. Evidence: `docs/track-011-rbc-p003-review-packet.md`.

## Phase 3 — Analysis

- [x] Build public/synthetic fixtures and analysis specification. Evidence: `examples/analyses/bronchiectasis-synthetic.yml` and `docs/bronchiectasis-011-reference.md`; empirical activation remains blocked.
- [x] Run primary and alternative hierarchy models. Evidence:
  `rareburden.demonstrators.run_bronchiectasis_synthetic_scenarios` and
  `tests/test_track011_bounded_reconciliation.py`; outputs remain synthetic-only.
- [x] Propagate overlap, unclassified-cause and transport uncertainty. `[M-06]`
  Evidence: bounded scenario reference range and fail-closed bounds in
  `tests/test_track011_bounded_reconciliation.py`; no empirical transportability
  claim is made.
- [x] Produce synthetic country/setting examples without unsupported extrapolation. Evidence: `docs/bronchiectasis-011-reference.md`.

## Phase 4 — Validation and release

- [x] Compare with independent registry/cohort evidence where possible. `[S-10]` Evidence: `docs/track-011-reference-closeout-2026-09-05.md` formalizes the documented applicability and non-comparability assessment; tertiary referral registries cannot validate fictional population quantities.
- [x] Complete repository engineering/scientific-language panel preparation and record unresolved gates. Evidence: `conductor/tracks/011-bronchiectasis-demonstrator/review.md`.
- [x] Produce reproducible synthetic reference report and limitations. Evidence: `docs/bronchiectasis-011-reference.md`.
- [x] Record accountable approval, narrowing or redesign decision under ADR-0009. Evidence: simulated role-separated advisory panel passed all four lanes (`docs/reviews/track-011-reference-output-panel-2026-09-05.yml`) and owner recorded Option A disposition (`docs/decisions/2026-09-05-track-011-owner-reference-disposition.yml`).

## Dependency review — 2026-07-27

- [x] Record that Track 011 cannot activate until Tracks 008, 009 and 010 are complete. Evidence: `380db83`.
- [x] Add non-binding RBC-P003 v0.1.0 protocol draft to the specification; activation and contract freeze remain blocked.

## Preparation refresh — 2026-08-01

- [x] Prepare the RBC-P003 review packet with denominator, aetiology, overlap,
  transportability, outcome and framing decisions. Evidence:
  `docs/track-011-rbc-p003-review-packet.md`; dependencies and respiratory,
  methods, engineering and patient/community review remain open.
- [x] Prepare the non-binding RBC-P003 protocol draft and denominator decision
  fields; clinical scope freeze and registration remain open.

## Preparation refresh — 2026-08-02

- [x] Add a fixture contract check for synthetic-only intent, independent
  dependence labelling and the no-extrapolation boundary. Evidence:
  `tests/test_downstream_track_contracts.py`; respiratory, scientific and
  patient/community gates remain open.

## Bounded dependency reconciliation — 2026-08-16

- [x] Bind the synthetic demonstrator to exact Track 008, 009 and 010 artifacts,
  with empirical activation, clinical interpretation and contract freeze kept
  false. Evidence: `docs/track-011-dependency-bindings-2026-08-16.yml`.
- [x] Reconcile a deterministic synthetic composition while retaining
  multi-aetiology, unknown and unaccounted groups as separate structural
  quantities. Evidence:
  `manifests/demonstrators/track-011-bounded-synthetic-receipt-2026-08-16.json`.
- [x] Add negative tests for activation claims, incomplete context and
  over-allocation beyond the denominator. Evidence:
  `tests/test_track011_bounded_reconciliation.py`.
- [x] Record bounded synthetic reference freeze for RBC-P003 under ADR-0009 owner disposition. Evidence: `docs/track-011-rbc-p003-bounded-registration-2026-09-05.yml` and `docs/track-011-reference-closeout-2026-09-05.md`; empirical activation, clinical interpretation and publication remain false.

## Synthetic reference demonstrator completion — 2026-09-05

- [x] Register bounded RBC-P003 protocol. Evidence: `docs/track-011-rbc-p003-bounded-registration-2026-09-05.yml`.
- [x] Execute reference pipeline, verify conservation accounting and export report/results/tables. Evidence: `src/rareburden/demonstrator_bronchiectasis.py`, `results/track-011-reference-2026-09-05/`, and `manifests/demonstrators/track-011-reference-execution-2026-09-05.json`.
- [x] Pass simulated role-separated advisory panel review and record owner reference disposition under ADR-0009. Evidence: `docs/reviews/track-011-reference-output-panel-2026-09-05.yml` and `docs/decisions/2026-09-05-track-011-owner-reference-disposition.yml`.
- [x] Complete synthetic reference closeout. Evidence: `docs/track-011-reference-closeout-2026-09-05.md`.
