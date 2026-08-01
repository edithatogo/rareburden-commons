# Track 005 plan

## Phase 1 — Method and governance

- [x] Draft RBC-P001D and define health-system, household and societal perspectives. `[S-06]` Evidence: non-binding reference contract in `docs/economic-social-005-reference.md`; registration and co-design remain open.
- [ ] Co-design component taxonomy with patient/family representatives. `[M-16]`
- [x] Define currency, price year, PPP, discounting and transfer-payment rules. Evidence: explicit transformation and transfer rules in the non-binding reference contract; health-economic approval remains open.
- [x] Define acceptable-use and burden-framing safeguards. Evidence: survey, remuneration, accessibility and no-collection safeguards in the non-binding reference contract; ethics and patient/community review remain open.

## Phase 2 — Data contracts

- [ ] Add cost, time, productivity, education and social-burden parameter schemas. `[M-18]`
- [ ] Define component overlap and missingness rules. `[M-05]`
- [ ] Define survey core, adaptation, translation and remuneration requirements.
- [ ] Define distributional subgroup and equity outputs.

## Phase 3 — Reference implementation

- [ ] Implement component calculations and declared-perspective validation.
- [ ] Add price/currency conversion interfaces with provenance.
- [ ] Add uncertainty and scenario propagation. `[M-06]`
- [ ] Build synthetic examples and golden tests.

## Phase 4 — Demonstrator integration

- [ ] Integrate appropriate components into monogenic-diabetes analysis.
- [ ] Specify linked administrative-cost inputs for paediatric analysis.
- [ ] Produce patient/family data-gap and new-collection plan. `[M-26]`
- [ ] Complete health-economics, ethics and patient/community review.

## Dependency review — 2026-07-27

- [x] Record that Track 005 cannot activate until Tracks 009 and 010 are complete. Evidence: `749a434`.
- [x] Add non-binding RBC-P001D v0.1.0 protocol draft to the specification; activation and contract freeze remain blocked.
