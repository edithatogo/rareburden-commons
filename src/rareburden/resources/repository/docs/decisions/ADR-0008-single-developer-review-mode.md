# ADR-0008: Single-developer review mode

**Status:** accepted by repository owner — 2026-08-02

## Context

RareBurden Commons is operated as a single-developer repository. Requiring a
second maintainer or internal human reviewer would be inaccurate and would not
improve the repository-owned evidence boundary.

## Decision

All repository-owned review, challenge, consistency checking, and draft
disposition work is routed to a panel of subagents. Track plans and review
packets should describe that panel as the internal review mechanism, including
its roles, dissent, findings, and commit/evidence binding.

No track may claim a second maintainer, internal human review, or constituted
committee that does not exist.

## Preserved external gates

This decision does not redefine evidence that inherently requires independence
or accountable authority: scientific suitability, patient/community authority,
data-custodian terms, independent operator reproduction, named operational
ownership, and release authority remain external gates. Subagent panels prepare
those packets and recommendations but cannot self-certify them.

## Consequences and fallback

The repository can continue autonomously through synthetic tests, panel review,
documentation, and bounded scope decisions. If an external gate is unavailable,
the affected claim or capability remains provisional, is narrowed, or is
removed; the track is not falsely completed.
