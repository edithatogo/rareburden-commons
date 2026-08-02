# Repository-owner approval — external-gate options

**Decision date:** 2026-08-03  
**Decision owner:** repository owner  
**Status:** approved repository scope; external/accountable receipts remain pending

## Candidate and receipt workflow decision

The repository owner approves **Option A — narrow, digest-bound release
candidate** from
`docs/frozen-candidate-and-receipts-decision-plan-2026-08-03.md`. The project
will freeze a bounded synthetic/public-data candidate before requesting the
six qualifying receipts, and will use the pending-register and fail-closed
validators for intake. Option B is permitted only if the candidate is already
frozen and every gate packet is independently scoped; Option C is the default
fallback when an accountable authority or lawful evidence is unavailable.

This is approval of the workflow and bounded preparation only. It does not
freeze a commit, create a release manifest, or convert any pending receipt into
an approved gate.

The repository owner approves the recommended bounded defaults for the
scientific, custodian/data-governance, Track 007 registration/challenge,
independent-operator, operational-ownership and release lanes:

- approve only exact, hash-bound source records with explicit metric,
  denominator, coverage and limitations;
- use metadata/hash retention, ephemeral retrieval, no raw redistribution and
  aggregate-only outputs unless stricter terms apply;
- register the frozen Track 007 protocol where possible, otherwise keep it
  explicitly unregistered and provisional;
- require independent reproduction for any independent claim;
- use named primary/backup owners or retain bounded interim/no-support status;
- release v1 only after all required evidence exists, otherwise use bounded,
  revise or stop dispositions.

This approval authorises repository-owned preparation and scope narrowing. It
does not itself constitute:

- scientific or clinical review;
- patient/community authority or consent;
- custodian/data-governance terms;
- independent operator evidence;
- operational-owner acceptance; or
- release-authority approval.

Those receipts must still identify the applicable role/authority, conflicts or
independence basis, exact commit or manifest digest, conditions, dissent and
expiry. Until then, the affected tracks remain fail-closed and unreleased.

## Routing decision

The repository owner approves **Option A — secure role-separated routing** from
`docs/receipt-routing-and-response-plan-2026-08-03.md`. Each gate request should
be sent separately to its accountable authority/body, with raw or restricted
responses returned through an agreed secure channel and only redacted locator
metadata retained in Git. This approval does not identify recipients, create a
secure channel, send a request, or convert silence, panel preparation or owner
approval into a qualifying receipt.
