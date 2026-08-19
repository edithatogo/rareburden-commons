# Track 012 plan

> Repository-owned review uses the subagent panel under ADR-0008; paediatric, privacy, custodian and patient/community authority remain separate.

## Phase 1 — Protocol and access pathways

- [ ] Freeze RBC-P004 person-level and aggregate estimands.
- [ ] Define Australian and New Zealand candidate data pathways and approvals.
- [ ] Define paediatric disease/coding package and observation windows.
- [ ] Obtain community/harm, Indigenous/data-use perspective and clinical-methods agent-panel review and owner disposition.

## Phase 2 — Synthetic linked-data model

- [x] Create synthetic person, diagnosis, admission, death and cost tables. `[C-03]` Evidence: `examples/paediatric/linked-data-synthetic.yml`.
- [x] Define person-level deduplication and multimorbidity rules. `[M-05]` Evidence: fixture rules and `docs/paediatric-012-reference.md`; implementation against controlled data remains gated.
- [ ] Implement utilisation, mortality and cost estimands.
- [x] Add small-cell disclosure case and export rule. Evidence: synthetic fixture disclosure rule; custodian threshold and inferential controls remain external-gated.

## Phase 3 — Federated package

- [ ] Integrate the Track 004 node runner.
- [ ] Add local code-list mapping and data-quality diagnostics.
- [ ] Define approved aggregate export tables and suppression.
- [ ] Write custodian application and operator materials.

## Phase 4 — Validation and portability

- [ ] Complete synthetic end-to-end execution.
- [ ] Seek approved local pilot or publish a pilot-ready protocol only.
- [ ] Specify replication in a differently governed country/node.
- [ ] Complete scientific, economic, privacy and community/harm agent-panel review and owner disposition.

## Dependency review — 2026-07-27

- [x] Record that Track 012 cannot activate until Tracks 004, 005, 008, 009 and 010 are complete. Evidence: `ff48477`.
- [x] Add non-binding RBC-P004 v0.1.0 protocol draft to the specification; activation and contract freeze remain blocked.

## Preparation refresh — 2026-08-01

- [x] Prepare the RBC-P004 review packet with estimand, coding, linkage,
  custodian/Indigenous governance, privacy, economic, patient/family and
  replication decisions. Evidence:
  `docs/track-012-rbc-p004-review-packet.md`; dependencies and external gates
  remain open.
- [x] Prepare the non-binding RBC-P004 protocol draft and estimand decision
  fields; access approvals and contract freeze remain open.

## Preparation refresh — 2026-08-02

- [x] Add a fixture contract check preserving multimorbidity rows and the
  custodian small-cell disclosure boundary. Evidence:
  `tests/test_downstream_track_contracts.py`; paediatric, privacy, custodian,
  economic and patient/community gates remain open.

## Bounded dependency reconciliation — 2026-08-16

- [x] Bind the synthetic linked-data exercise to exact Track 004, 005 and
  008–011 repository artifacts while keeping controlled-data, clinical, policy
  and contract activation false. Evidence:
  `docs/track-012-dependency-bindings-2026-08-16.yml`.
- [x] Produce a deterministic synthetic receipt for deduplicated people,
  multimorbidity, utilisation, missing mortality/cost fields, suppressed
  jurisdiction breakdowns and explicit non-imputation. Evidence:
  `manifests/demonstrators/track-012-bounded-synthetic-receipt-2026-08-16.json`.
- [x] Add fail-closed tests for activation, referential-integrity failures,
  duplicate people and unsafe disclosure thresholds. Evidence:
  `tests/test_track012_bounded_reconciliation.py`.
- [ ] Activate or freeze RBC-P004 only after approved real-data pathways,
  coding and estimands, transportability evidence, panel findings and owner
  disposition exist; synthetic reconciliation does not satisfy those gates.
