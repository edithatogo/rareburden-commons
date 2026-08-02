# External gate register — Track 017 release candidate

**Status:** template; all gates are pending. This file is not evidence of
approval, consent, independence, custody, operational acceptance, or release.

Bind every receipt to the exact candidate commit, manifest identifier, and
artifact digest. A technical test or subagent report may support a receipt but
cannot replace the accountable decision-maker.

| Gate | Required accountable role | Status | Receipt / next action | Minimum receipt |
| --- | --- | --- | --- | --- |
| Scientific methods | Independent methods reviewer | `pending` | Not received; route `scientific` template | Identity/organisation, independence and conflicts, protocols/evidence reviewed, disposition, conditions, dissent, residual-risk owner, expiry |
| Patient/community | Constituted patient/community reviewer(s) | `pending` | Not received; route `patient_community` template | Remit, participants/quorum, acceptable-use and harm decision, permitted wording, dissent, review date |
| Data governance/custodian | Named custodian or governance authority | `pending` | Not received; route `custodian_data_governance` template | Lawful basis, source terms, retention/withdrawal, redistribution, disclosure thresholds, pilot/rollback conditions |
| Independent operator | Operator not responsible for implementation | `pending` | Not received; route `independent_operator` template | Clean-checkout environment, exact digest, commands, outputs, defects, usability/reproduction receipt |
| Operational ownership | Named primary and backup owners | `pending` | Not received; route `operational_owners` template | Support scope, escalation, backup/restore/rollback, incident duties, capacity, expiry, acceptance |
| Release authority | Owner or constituted release authority | `pending` | Not received; route `release` template | Final `release`/`bounded`/`revise`/`stop`, exact digest, permitted scope, exclusions, conditions, review date |

## Fail-closed rules

- Missing, expired, conflicting, or digest-mismatched receipts leave the gate
  `pending`.
- Owner/release-authority approval is recorded separately from independent
  scientific, patient/community, custodian, and operator evidence.
- A receipt is accepted into this register only after an accountable submitter
  provides a unique receipt ID, exact candidate identity, decision timestamp,
  authority/independence basis, and a durable approval record. Superseded or
  expired receipts remain retained but cannot clear a gate.
- The register is updated by the repository maintainer after checking the
  receipt for completeness and digest match; that administrative check does
  not become the underlying accountable decision.
- Until the relevant gates are recorded, exclude controlled data, custodian
  deployment, global or unsupported comparative claims, patient-facing policy
  conclusions, production support promises, and stable-v1 publication.
