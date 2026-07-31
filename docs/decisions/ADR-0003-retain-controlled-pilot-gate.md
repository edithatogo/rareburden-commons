# ADR-0003 — Retain the controlled-environment pilot gate

**Status:** Accepted  
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

RareBurden Commons retains the controlled-environment pilot as a blocking v1 gate.
Synthetic and offline evidence must not be described as a pilot, custodian
approval, partnership, or controlled-data capability.

The release-scope decision will be reconsidered after Tracks 009 and 010 are
complete and before the first v1 release-candidate decision. At that checkpoint:

- retain the gate when a lawful custodian pathway and accountable reviewers exist;
- otherwise record a new bounded-scope decision and remove claims requiring
  controlled data before release.

## Consequences

- Track 004 remains blocked despite its bounded synthetic implementation passing.
- No controlled node may be activated without documentary governance, security,
  scientific, patient/community and custodian approval.
- The product promise is not narrowed prematurely.
- v1 cannot pass V1-FED-04 through limitations text or synthetic evidence alone.
