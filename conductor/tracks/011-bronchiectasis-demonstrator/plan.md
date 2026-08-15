# Track 011 plan

> Repository-owned review uses the subagent panel under ADR-0008; respiratory clinical and patient/community review remains separate.

## Phase 1 — Protocol and semantic scope

- [ ] Define and freeze bronchiectasis denominator populations.
- [ ] Define included rare aetiologies and ontology versions. `[M-01, M-02]`
- [ ] Define multi-aetiology, unclassified and overlapping categories. `[M-05]`
- [ ] Obtain respiratory-methods and community/harm agent-panel review and owner disposition.

## Phase 2 — Evidence and transportability

- [ ] Extract aetiologic-fraction evidence by age, setting and diagnostic capacity.
- [ ] Ledger outcomes, delay and service use with quality grades. `[M-21]`
- [ ] Model referral, testing and case-definition bias.
- [ ] Specify geography and health-system transfer scenarios.

## Phase 3 — Analysis

- [x] Build public/synthetic fixtures and analysis specification. Evidence: `examples/analyses/bronchiectasis-synthetic.yml` and `docs/bronchiectasis-011-reference.md`; empirical activation remains blocked.
- [ ] Run primary and alternative hierarchy models.
- [ ] Propagate overlap, unclassified-cause and transport uncertainty. `[M-06]`
- [ ] Produce country/setting examples without unsupported extrapolation.

## Phase 4 — Validation and release

- [ ] Compare with independent registry/cohort evidence where possible.
- [ ] Complete scientific and language agent-panel review and owner disposition.
- [x] Produce reproducible synthetic reference report and limitations. Evidence: `docs/bronchiectasis-011-reference.md`.
- [ ] Record approval, narrowing or redesign decision.

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
- [ ] Freeze or activate RBC-P003 only after a real denominator, empirical
  aetiology evidence, transportability assessment and owner disposition exist;
  the bounded synthetic receipt does not satisfy these gates.
