# Track 012 dependency review — Collective paediatric rare-disease burden demonstrator

**Review date:** 2026-07-27  
**Decision:** Blocked pending Tracks 004, 005, 008, 009 and 010

## Findings

- Tracks 004 and 005 are blocked, and Tracks 008, 009 and 010 are also blocked.
- No approved paediatric protocol, data pathway, synthetic linked-data model, federated integration or disclosure package has been completed; only a non-binding protocol draft exists.
- Paediatric, clinical, economic, privacy, data-governance, security and patient/community gates remain required.

Repository-owned preparatory work now includes an entirely synthetic linked-data
fixture covering person, diagnosis, admission, death and cost tables, with
multimorbidity retention, duplicate-admission handling and disclosure-boundary
rules. It contains no real or controlled data.

### Review rerun — 2026-07-29

Repository review result: **Pass with dependency and governance gates**. The
fixture and reference documentation are bounded and reproducible, and the full
validation gate passes. Track 012 remains blocked pending Tracks 004, 005,
008–010 and paediatric, privacy, Indigenous/data-governance, security,
patient/family and engineering review.

## Disposition

Keep Track 012 **blocked**. Do not activate controlled-data or paediatric burden work until all prerequisite contracts and approvals are available.

### External reviewer packet

- **Paediatric/clinical/economic:** approve estimands, coding, observation windows, utilisation, mortality and cost interpretation.
- **Privacy/data governance/security:** approve custodian pathway, linkage authority, Indigenous governance, suppression, retention and incident controls.
- **Patient/family:** assess acceptable use, equity, language and harms.
- **Evidence required:** approved pathway record, synthetic linked-data run, disclosure tests, export specification, review comments and dissent disposition.
