# ADR-0007: External-gate handling and bounded candidate policy

**Status:** approved scope policy; not a release authorization  
**Date:** 2026-08-01

## Decisions

1. Continue preparation of a public/synthetic release candidate while external
   gates are open.
2. Treat subagent audits and reproductions as preparatory technical evidence;
   they do not replace scientific, patient/community, data-governance,
   custodian, programme or release-authority decisions.
3. Permit a time-limited interim-owner model for bounded preparation, with an
   explicit expiry and reduced support promise, if no institutional host is yet
   available.
4. If an authority-sensitive review is unavailable, remove the affected claim
   or capability and retain the gate as open. Do not convert absence of review
   into approval.

## Standing exclusions

Until the relevant receipts are recorded, the candidate excludes controlled
data and custodian deployment, global representativeness, unsupported country
comparisons, patient-facing policy conclusions, institutional support promises
and stable-v1 publication.

## Required evidence for reconsideration

The external-gate packet must contain dated decisions, named accountable roles,
candidate commit and artefact digests, conditions, dissent, residual-risk
owners and review dates. Reconsideration may result in `release`, `bounded`,
`revise` or `stop`; this ADR does not preselect that outcome.
