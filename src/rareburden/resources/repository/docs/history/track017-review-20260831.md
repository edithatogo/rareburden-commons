# Track 017 dependency review — Documentation, adoption and stable v1

## Bounded integrity maintenance — 2026-08-31

Registry, setup state, canonical track indexes and task-state regression checks
are reconciled in `docs/conductor-integrity-reconciliation-2026-08-31.md`.
The advisory engineering, governance and simulated-community/usability lanes
recorded accept recommendations in
`docs/reviews/conductor-integrity-2026-08-31.yml`, conditional on full validation
and hosted integration checks. Governance feedback corrected Track 014's stale
review notice/date; usability feedback clarified the self-assessment label.
This adds one bounded maintenance task: 27 completed preparation tasks and 17
pending tasks. Track 017 remains Planned; no stable-release gate is closed.
Historical dated reviews below are retained unchanged.

Hosted follow-up (PR #277): the checker now compares title, priority, target,
owner and dependencies as well as status and index. Setup state has explicit
`in_review_tracks` and `proposed_tracks` inventories, both currently empty.
Transition regressions prove neither lifecycle state can disappear from the
projection. Exact follow-up bindings and 35 focused passing tests are recorded
in `docs/reviews/conductor-integrity-hosted-followup-2026-08-31.yml`.

**Review date:** 2026-08-20
**Decision:** Bounded repository preparation; stable release not activated

## Findings

- Tracks 013–016 are incomplete, so Track 017 cannot enter Ready or close the
  stable-v1 acceptance contract.
- Role-separated usability-agent assessments, two clean candidate builds, one
  owner-operated reproduction and a bounded exact-candidate owner disposition
  are complete as repository evidence.
- Backup continuity, sustainability, remaining v1 criteria, a later stable
  release decision and post-decision public verification remain open.
- Tagging v1 or making a stable support promise now would violate the release
  contract.

## Local preparation

`docs/v1-adoption-017-reference.md` defines role-based documentation coverage,
release-evidence lanes and the clean-reproduction checklist. It is preparatory
and does not imply human usability, support, institutional hosting or stable
release approval.

The repository-owned documentation slice is present in `docs/guides/`, with an
offline synthetic reference tutorial at `docs/tutorial-reference-workflow.md`
and accessibility, citation, licence and correction guidance at
`docs/documentation-guidance-017.md`. The markdown-link check and full local
validation pass; these results do not create independent or external authority.

## Review fixes — 2026-08-01

The initial review found that “quickstart” and “methods” were only indirect
links. Explicit navigable guides were added at `docs/guides/quickstart.md` and
`docs/guides/methods.md`; runtime assets were regenerated and the full check
passed with 429 tests. No release claim was changed.

## Activation gates

- Complete Tracks 013–016 and link every blocking v1 criterion.
- Retain the two role-separated usability-agent reports, two clean release
  candidates and separately recorded owner-operated reproduction with
  equivalent outputs as exact-candidate repository evidence.
- Complete the maintainer/backup roster, sustainability model and institutional
  host or bounded interim ownership.
- Complete agent-panel challenge, repository-owner stable disposition and
  public artefact verification before v1.0.0 tagging.

## Preparation refresh — 2026-08-01

`docs/track-017-v1-closeout-packet.md` defines the exact receipts and
accountable decisions needed for agent usability, owner reproduction,
operational ownership, cross-track governance and release integrity. It is
preparatory only; no stable-v1 tag, support promise or publication authority is
asserted.

## Bounded reconciliation review — 2026-08-16

The manifest, validator and negative tests bind current Track 013–016 evidence,
preserve the incomplete backup-continuity state, and prevent agent advice or
repository checks from becoming independent/external approval or stable-v1
claims. Repository preparation passes review. Track 016 is exactly bound at PR
#104 merge `18910840fee787bbe2ae7d7eff40b944539a11f4`; support continuity,
public verification and stable-release gates stay open.

## Exercise review — 2026-08-16

Two role-separated advisory agent assessments, two clean locked candidate
builds and one owner-operated clean-environment reproduction were executed
against exact commit `3cfdf8dee5aa7440b936f03ac171fb95665b5f8b`.
The first-time-user assessment found that the documented bare `python` command
failed in the clean environment. The guides now use `uv run python` and include
prerequisites, resource expectations, navigation and fail-closed
troubleshooting. Repeated generation and verification passed; all three output
manifests and verifier reports were identical. These are repository and agent
advisory receipts only—not human accessibility conformance, independent
reproduction, backup continuity, external approval or stable-release evidence.

## Evidence-index review — 2026-08-16

All 67 stable-v1 acceptance criteria are enumerated in a hash-bound index with
evidence routes and explicit group gaps. The validator rejects omitted,
duplicated or reordered criteria, hash drift, unbound evidence and release
overclaims. Index completeness is an accounting property only: no criterion is
promoted to satisfied, and stable acceptance remains incomplete. Qualifying
backup continuity and post-decision public stable-artifact verification remain
pending; the later exact-candidate owner disposition is bounded, not stable.

## Owner bounded-disposition review — 2026-08-16

The repository owner recorded an immutable GitHub receipt for exact candidate
`ba92940572bd69e19d54447e59b8ba8f776e3d5b`: bounded synthetic/public preview,
stable release deferred. The receipt accepts repository tests, advisory agent
findings and owner-operated reproduction while retaining source-rights,
coverage, continuity, external-authority and support exclusions. Its validator
prevents promotion to production, stable release, a v1 tag, independent or
external approval, backup continuity or public stable-artifact verification.

## Evidence-contract reconciliation review — 2026-08-20

PR #134 replaced the evidence-bearing plan and review with an older draft,
reducing the plan from 24 completed tasks to five and reopening work already
bound to immutable manifests. PR #136 corrected the single-owner wording but
did not restore the lost evidence history.

This reconciliation restores that append-only history, retains the ADR-0009
agent-panel and owner model, and adds a regression test for the exact evidence
markers and minimum completed-task count. The plan now records 26 completed and
17 pending tasks. Track 017 remains **Planned** because dependencies 013–016
and the remaining stable-release gates are unresolved; it is not
archive-eligible and v1.0.0 remains disabled.

## Bounded single-owner continuity disposition — 2026-08-20

The owner accepts the single-point-of-failure limitation for the bounded
non-production synthetic/public candidate. Redundant backup ownership is
non-applicable to this exact candidate, not completed. Existing owner-operated
recovery, rollback, correction and withdrawal evidence remains repository
evidence only. A stable or production decision still requires qualifying
continuity evidence or a new exact-candidate risk decision, and no stable
support promise is made here.

## Bounded retained-reference guidance — 2026-08-31

Panel assurance: simulated role-separated advisory panel. The documentation
author checked consistency; separate engineering and security/novice-user agents
challenged the route and its claims. All bound candidate
`1469a90951f7b920ffa98e09c2f7abe5869868bc`, tree
`ef85cdbe300247820000f6d8b7cbfd58efa50022`, to
`manifests/release/track017-retained-guidance-inputs-20260831.json` (SHA-256
`99f3daadcbfb1086a4811b18a076bccd7787a149ebf3222d827faec1e6f6fde5`).
No blocking finding or dissent remained for this documentation-only slice.

The owner-directed verifier invocation exited zero and all three retained output
hashes were identical before and after. It used `uv run --no-sync` in the already
provisioned environment: the same verifier entry point and arguments as the
guide, not a byte-for-byte test of the guide's outer environment synchronization.
The five new documentation-contract tests and 42 focused related tests passed.
No historical analysis was executed, no outputs or receipts were rewritten, and
the separate public-foundation generator was not used as Track 003 reproduction.

The recommendation is to accept the bounded guidance under the existing
continuation instruction, or defer it while retaining the older navigation.
Acceptance improves discoverability without changing scientific scope; deferral
preserves ambiguity between the two workflows. Minimum evidence is the exact
reviewed guidance, successful non-executing verification, unchanged historical
hashes and passing documentation/link checks. Stop on missing full-checkout
resources, hash mismatch, regeneration instructions or expanded empirical,
clinical, community or release claims. Human usability, empirical validity and
stable release readiness remain unestablished.

Owner-executed simulated-community challenge; no actual community participation,
representation, consultation, endorsement, consent or independent review.

Only two new preparation tasks close: the plan now has 29 completed preparation
tasks and the original 17 pending tasks. Track 017 remains Planned; no stable
release, support obligation, owner-risk disposition or original release gate is
promoted. The evidence-recording commit is later than the reviewed guide candidate.
