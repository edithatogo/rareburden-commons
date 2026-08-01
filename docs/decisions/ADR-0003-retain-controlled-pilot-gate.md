# ADR-0003 — Retain the controlled-environment pilot gate

**Status:** Superseded for v1 scope by ADR-0005  
**Date:** 2026-07-31

## Context

V1-FED-04 requires either an approved controlled-environment pilot or an explicit
decision excluding claims that require controlled data. The repository now has a
bounded synthetic runner, disclosure controls, reproducibility evidence and a
non-binding pilot packet, but it has no custodian authorisation or controlled
execution evidence.

Removing controlled-data claims now would materially narrow the product promise
before the evidence-ledger and burden-engine dependencies are complete.

## Decision

RareBurden Commons retained the controlled-environment pilot as a blocking v1
gate at the time of this decision. ADR-0005 subsequently bounds the stable v1
scope to public and synthetic evidence and moves the pilot to a post-v1
milestone. Synthetic and offline evidence must not be described as a pilot,
custodian approval, partnership, or controlled-data capability.

The release-scope decision will be reconsidered after Tracks 009 and 010 are
complete and before the first v1 release-candidate decision. At that checkpoint:

- retain the gate when a lawful custodian pathway and accountable reviewers exist;
- otherwise record a new bounded-scope decision and remove claims requiring
  controlled data before release.

## Consequences

- Track 004 remains externally gated for any post-v1 controlled pilot despite its
  bounded synthetic implementation passing.
- No controlled node may be activated without documentary governance, security,
  scientific, patient/community and custodian approval.
- The product promise is not narrowed prematurely.
- The superseding bounded-scope decision, rather than limitations text or
  synthetic evidence alone, is the V1-FED-04 evidence for stable v1.
