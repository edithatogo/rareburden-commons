# Track 012 plan

## Phase 1 — Protocol and access pathways

- [x] Draft RBC-P004 with person-level and aggregate estimands. Evidence: non-binding estimand and pathway boundary in `docs/paediatric-012-reference.md`; no person-level access is authorized.
- [ ] Define Australian and New Zealand candidate data pathways and approvals.
- [x] Define paediatric disease/coding package and observation windows. Evidence: reference contract requires versioned coding, explicit index/look-back/look-forward windows and jurisdiction; actual coding package remains custodian-gated.
- [ ] Obtain patient/family, Indigenous/data-governance and clinical review.

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
- [ ] Complete scientific, economic, privacy and patient/community review.

## Dependency review — 2026-07-27

- [x] Record that Track 012 cannot activate until Tracks 004, 005, 008, 009 and 010 are complete. Evidence: `ff48477`.
- [x] Add non-binding RBC-P004 v0.1.0 protocol draft to the specification; activation and contract freeze remain blocked.
