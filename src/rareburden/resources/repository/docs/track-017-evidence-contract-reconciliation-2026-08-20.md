# Track 017 evidence-contract reconciliation

**Status:** repository evidence history restored; Track 017 remains Planned and
stable v1 remains disabled.
**Reconciliation date:** 2026-08-20

## Purpose

Restore Track 017 evidence lost when PR #134 replaced the evidence-bearing
plan and review with an older draft, and prevent stale issue or documentation
mirrors from redefining the accepted single-developer review contract.

## Authority order

1. `docs/decisions/ADR-0009-agent-panel-owner-governance.md` defines the
   single-developer operating model.
2. `docs/v1-acceptance-criteria.md` defines the stable-release contract.
3. Track 017 `spec.md`, `plan.md`, `metadata.json` and `review.md` define the
   track lifecycle and evidence.
4. Supporting plans, templates and GitHub issue bodies mirror those sources;
   they cannot reopen completed work or add an additional-person gate.

Role-separated agents provide advisory challenge. The repository owner records
the attributable disposition for an exact candidate. Agent or owner evidence is
never represented as independent, human, constituted-community, custodian,
licensor, institutional or external approval. Publisher rights and any future
controlled-data custodian terms remain factual constraints.

## Regression and restoration

Before PR #134, Track 017 recorded 24 completed and 18 pending tasks. PR #134
replaced that plan with an older five-completion, 20-pending draft. PR #136
corrected the independent-user wording but retained the lost task history.

This reconciliation restores:

- four completed role-guide and documentation tasks;
- four executed agent-usability, clean-build and owner-reproduction tasks;
- the complete, fail-closed 67-criterion evidence index;
- the exact-candidate bounded owner disposition;
- the bounded-readiness manifest, validator, negative tests and Track 016
  binding;
- the earlier preparation, schema, ownership-packet and review-fix records.

The reconciliation itself raises the plan to 25 completed and 18 pending tasks.
It does not close a stable-v1 criterion merely because its evidence is indexed.

## Current issue-mirror contract

GitHub issue #16 should report:

- Conductor status: `planned`;
- completed plan checkboxes: 25;
- in-progress plan checkboxes: 0;
- pending plan checkboxes: 18;
- role-separated usability-agent assessments: executed as advisory evidence;
- two clean candidates and one owner-operated reproduction: executed and
  hash-bound;
- exact-candidate owner decision: bounded synthetic/public preview, stable
  release deferred;
- remaining gates: dependencies 013–016, continuity, sustainability, remaining
  acceptance gaps, later stable disposition, publication and public
  verification.

The issue must not request independent users, an independent operator,
independent reproduction or additional-person sign-off. Updating the GitHub
issue remains a separate repository mutation and is not evidence created by
this local reconciliation.

## Status decision

Track 017 remains Planned. Its dependencies are incomplete, so it cannot enter
Ready or Active under `conductor/workflow.md`. Stable release, support
continuity, v1.0.0 tagging, publication and public verification remain
fail-closed.
