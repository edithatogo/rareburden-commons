# Track 011 plan

> Repository-owned review uses the subagent panel under ADR-0008; respiratory clinical and patient/community review remains separate.

## Phase 1 — Protocol and semantic scope

- [x] Define and bound bronchiectasis denominator populations for synthetic assurance. Evidence: `examples/demonstrators/011-bounded-synthetic-profile.yml`.
- [x] Define included rare aetiologies and ontology versions for the non-binding semantic fixture. Evidence: `examples/semantics/bronchiectasis-synthetic.yml`. `[M-01, M-02]`
- [x] Define multi-aetiology, unclassified and overlapping categories. Evidence: `manifests/demonstrators/track-011-bounded-synthetic-receipt-2026-08-16.json`. `[M-05]`
- [x] Complete repository-owned agent-panel preparation packet; clinical and community authority remain external gates. Evidence: `docs/track-011-rbc-p003-review-packet.md`.

## Phase 2 — Evidence and transportability

- [ ] Extract aetiologic-fraction evidence by age, setting and diagnostic capacity.
- [ ] Ledger outcomes, delay and service use with quality grades. `[M-21]`
- [x] Model referral, testing and case-definition bias in the bounded analysis specification. Evidence: `examples/analyses/bronchiectasis-synthetic.yml`.
- [x] Specify geography and health-system transfer scenarios without extrapolation. Evidence: `docs/track-011-rbc-p003-review-packet.md`.

## Phase 3 — Analysis

- [x] Build public/synthetic fixtures and analysis specification. Evidence: `examples/analyses/bronchiectasis-synthetic.yml` and `docs/bronchiectasis-011-reference.md`; empirical activation remains blocked.
- [x] Run primary and alternative hierarchy models on synthetic fixtures. Evidence: `tests/test_track011_bounded_reconciliation.py`.
- [x] Propagate overlap, unclassified-cause and transport uncertainty structurally. Evidence: `manifests/demonstrators/track-011-bounded-synthetic-receipt-2026-08-16.json`. `[M-06]`
- [x] Produce synthetic country/setting examples without unsupported extrapolation. Evidence: `docs/bronchiectasis-011-reference.md`.

## Phase 4 — Validation and release

- [ ] Compare with independent registry/cohort evidence where possible.
- [x] Complete repository engineering/scientific-language panel preparation and record unresolved gates. Evidence: `conductor/tracks/011-bronchiectasis-demonstrator/review.md`.
- [x] Produce reproducible synthetic reference report and limitations. Evidence: `docs/bronchiectasis-011-reference.md`.
- [ ] Record accountable approval, narrowing or redesign decision after empirical and clinical/community evidence.

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
