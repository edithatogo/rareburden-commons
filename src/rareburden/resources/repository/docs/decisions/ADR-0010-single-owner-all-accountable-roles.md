# ADR-0010: Single owner holds all accountable repository roles

**Status:** accepted by repository owner — 2026-08-21

## Context

RareBurden Commons is a single-developer repository. Discipline labels in
track metadata could be misread as separate office holders, and advisory agent
outputs were not uniformly required to present a complete decision analysis.

ADR-0009 remains historically immutable because existing evidence manifests
bind its exact bytes. This ADR extends that operating model prospectively.

## Decision

The repository owner, `edithatogo`, is the sole developer and holds every
accountable repository role, including methods, scientific, clinical-scope,
epidemiology, semantic, data-use, patient/community-perspective, equity/harm,
engineering, security, operations, programme and release decisions.

Role labels used by agent panels are challenge perspectives, not separate
office holders or delegated authority. Agents provide advice; the repository
owner decides. Every synthesis presented for an owner decision must include:

- options;
- trade-offs;
- contingencies;
- rationale; and
- a recommendation.

Advice also preserves evidence, uncertainty, dissent, residual risks and stop
triggers. The owner may accept, narrow, revise, defer or stop an exact
candidate. Agents cannot approve or decide on the owner's behalf.

The machine-readable contract is `docs/single-developer-governance.yml`.
Repository validation requires every track and the track register to identify
the repository owner as holder of all accountable repository roles.

## Independence and external-fact boundary

Owner-operated work and agent advice are not independent review. Any claim of
independence requires separate qualifying evidence. Publisher licences, source
terms, third-party rights, registry events, controlled-data custodian policies,
credentials and live-service capacity remain facts that neither the owner nor
agents can manufacture.

## Consequences

No additional person is a mandatory repository role. Distinct agent
perspectives remain useful for challenge but carry no authority. Historical
evidence is not relabelled, and unresolved critical findings still require
narrowing or stopping.
