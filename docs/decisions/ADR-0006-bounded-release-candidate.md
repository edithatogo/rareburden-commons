# ADR-0006: Continue bounded public/synthetic release preparation

**Status:** accepted as a scope-control decision; not a publication approval  
**Date:** 2026-08-01

## Decision

Continue technical release-candidate preparation using only public and
synthetic artefacts. Subagent reports may contribute preparatory evidence, but
they do not replace scientific, patient/community, data-governance, custodian
or release-authority decisions.

The preparation scope explicitly excludes:

- controlled-data execution or custodian deployment;
- global representativeness and unsupported country comparisons;
- patient-facing or policy conclusions requiring community review;
- institutional support or stable-v1 publication claims.

No `v1.0.0` tag, hosted API activation or public beta publication is authorised
by this ADR.

## Evidence rule

Subagent reproductions, security reviews and documentation audits are recorded
as preparatory evidence with the exact commit, environment, hashes and limits.
Authority-bound gates remain open until an accountable reviewer supplies a
dated decision and receipt.

## Reconsideration

Revisit this boundary only when the external-gate packet contains scientific,
patient/community, data-governance, programme and release decisions, and the
independent reproduction/usability receipts required by the v1 criteria.
