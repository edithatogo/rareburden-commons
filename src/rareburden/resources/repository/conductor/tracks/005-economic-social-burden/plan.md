# Track 005 plan

> Review routing (owner direction, 2026-08-22): clinical/scientific, patient/community and data-governance/custodian questions are sent to role-separated advisory agents and presented to the repository owner for disposition. Security/engineering approval is an explicit owner-operated decision lane. Agent advice and owner-operated evidence do not create independent, community or custodian approval.

## Phase 1 — Method and governance

- [ ] Draft RBC-P001D and define health-system, household and societal perspectives. `[S-06]`
- [ ] Challenge component taxonomy with community/harm perspective agents and owner disposition. `[M-16]`
- [ ] Define currency, price year, PPP, discounting and transfer-payment rules.
- [ ] Define acceptable-use and burden-framing safeguards.

## Phase 2 — Data contracts

- [ ] Add cost, time, productivity, education and social-burden parameter schemas. `[M-18]`
- [ ] Define component overlap and missingness rules. `[M-05]`
- [ ] Define survey core, adaptation, translation and remuneration requirements.
- [ ] Define distributional subgroup and equity outputs.

## Phase 3 — Reference implementation

- [ ] Implement component calculations and declared-perspective validation.
- [ ] Add price/currency conversion interfaces with provenance.
- [ ] Add uncertainty and scenario propagation. `[M-06]`
- [x] Build a non-binding synthetic cost-ledger example and schema test. Evidence: `examples/ledger/economic-social-synthetic.yml`; perspective, price-year and valuation contracts remain unresolved. 

## Phase 4 — Demonstrator integration

- [ ] Integrate appropriate components into monogenic-diabetes analysis.
- [ ] Specify linked administrative-cost inputs for paediatric analysis.
- [ ] Produce patient/family data-gap and new-collection plan. `[M-26]`
- [ ] Complete health-economics, ethics and community/harm agent-panel review and owner disposition.

## Dependency review — 2026-07-27

- [x] Record that Track 005 cannot activate until Tracks 009 and 010 are complete. Evidence: `749a434`.
- [x] Add non-binding RBC-P001D v0.1.0 protocol draft to the specification; activation and contract freeze remain blocked.

## Preparation refresh — 2026-08-01

- [x] Prepare the economic/social burden review packet with perspective,
  valuation, overlap, missingness, distributional and co-design decisions.
  Evidence: `docs/track-005-economic-review-packet.md`; dependencies and
  health-economics, ethics, governance and patient/community review remain open.

## GHED source-selection readiness — 2026-08-21

- [x] Prepare a requirements-only WHO GHED selection-readiness packet. Evidence:
  `docs/track-005-ghed-selection-readiness-2026-08-21.yml`; the exact release,
  file, indicators, terms and scientific fitness remain unselected or unresolved,
  and no bytes were retrieved, retained, activated or authorized for publication.
