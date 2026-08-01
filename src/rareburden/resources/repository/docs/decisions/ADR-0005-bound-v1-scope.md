# ADR-0005 — Bound v1 to public and synthetic evidence

**Status:** Accepted  
**Date:** 2026-08-01  
**Supersedes:** The v1-gate portion of ADR-0003

## Context

The repository has a deterministic synthetic federated-node implementation and
non-binding controlled-environment materials, but no custodian authorisation,
controlled data, independent operator receipt, or completed controlled pilot.
Those gates require external people, institutions and decisions.

## Decision

The stable v1 scope explicitly excludes claims that require controlled data,
custodian authority, or a controlled-environment pilot. Public-source,
synthetic and offline evidence remain in scope. The controlled pilot is retained
as a post-v1 milestone and may not be described as completed by synthetic tests,
offline execution, or same-operator evidence.

## Consequences

- V1-FED-04 is satisfied only by this bounded-scope decision, not by a pilot
  receipt.
- Track 004 may complete its public/synthetic v1 slice while retaining the
  post-v1 pilot gate.
- A future pilot still requires data-governance, patient/community, scientific,
  privacy, security, engineering, custodian and independent-operator evidence.
- Stable v1 remains blocked by the other acceptance criteria, including
  independent reproduction, operational exercises, named backup ownership and
  release-bound evidence.
