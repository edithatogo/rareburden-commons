# ADR-0002 — Gate-based release train to stable v1.0

**Status:** Accepted  
**Date:** 2026-07-19

## Context

The foundation repository described a five-year programme and a small set of proposed tracks, but it did not provide a complete implementation sequence or an objective definition of a stable v1.0. This created a risk that maturity would be inferred from documentation volume, a single demonstrator or a polished atlas rather than scientific, governance, security and operational evidence.

## Decision

RareBurden Commons will use a gate-based release train from v0.2.0 to v1.0.0.

- Every material capability is assigned to a Conductor track with specification, plan, metadata and review.
- Every track is assigned to one primary release and dependency-checked.
- Release progression is based on acceptance evidence rather than calendar dates.
- Stable v1.0 has a blocking multi-domain acceptance contract.
- Scientific, patient/community, data-governance, engineering, security and release reviews can each block a release.
- Unsupported capabilities are removed from the product promise rather than waived through limitations text.

The machine-readable roadmap and track metadata are validated in CI.

## Consequences

### Positive

- The critical path and missing capabilities are explicit.
- Programme strategy, scientific work and software delivery share one control system.
- External partners and funders can see bounded work packages and decision gates.
- The stable label has a defensible meaning.
- Drift between track metadata and the release plan can fail automated checks.

### Costs

- More planning and review artefacts must be maintained.
- Some attractive outputs will be delayed until provenance and validation are ready.
- A release may be narrowed or stopped when a blocking assurance lane is unresolved.

### Risks

- The process could become bureaucratic. Mitigation: requirements and evidence should be concise, machine-readable where useful and proportionate to risk.
- Track numbering does not equal execution order because previously proposed tracks retain their identifiers. Mitigation: dependencies and target releases are authoritative.
