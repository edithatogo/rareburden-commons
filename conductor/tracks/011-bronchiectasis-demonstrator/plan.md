# Track 011 plan

## Phase 1 — Protocol and semantic scope

- [ ] Draft RBC-P003 and define bronchiectasis denominator populations.
- [ ] Define included rare aetiologies and ontology versions. `[M-01, M-02]`
- [ ] Define multi-aetiology, unclassified and overlapping categories. `[M-05]`
- [ ] Obtain respiratory and patient/community review.

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
- [ ] Complete external scientific and language review.
- [x] Produce reproducible synthetic reference report and limitations. Evidence: `docs/bronchiectasis-011-reference.md`.
- [ ] Record approval, narrowing or redesign decision.

## Dependency review — 2026-07-27

- [x] Record that Track 011 cannot activate until Tracks 008, 009 and 010 are complete. Evidence: `380db83`.
- [x] Add non-binding RBC-P003 v0.1.0 protocol draft to the specification; activation and contract freeze remain blocked.
