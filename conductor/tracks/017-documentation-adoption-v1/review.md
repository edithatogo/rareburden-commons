# Track 017 dependency review — Documentation, adoption and stable v1

**Review date:** 2026-07-29  
**Decision:** Planned; stable-release work not activated

## Findings

- Tracks 013–016 are incomplete, so the v1 evidence index cannot be closed.
- No independent user, node-operator, reproduction, cost-model, institutional
  host or multi-lane release sign-off exists.
- Tagging v1 or making a support promise now would violate the release contract.

## Local preparation

`docs/v1-adoption-017-reference.md` defines role-based documentation coverage,
release-evidence lanes and the clean-reproduction checklist. It is preparatory
and does not imply usability, support, institutional hosting or release approval.

The repository-owned documentation slice is now present in `docs/guides/`, with
an offline synthetic reference tutorial at `docs/tutorial-reference-workflow.md`
and accessibility, citation, licence and correction guidance at
`docs/documentation-guidance-017.md`. The markdown-link check and full local
validation pass; these results do not substitute for independent users,
operators, reproduction or accountable review.

## Review fixes — 2026-08-01

The initial review found that “quickstart” and “methods” were only indirect
links. Explicit navigable guides were added at `docs/guides/quickstart.md` and
`docs/guides/methods.md`; runtime assets were regenerated and the full check
passed with 429 tests. No external-gate claim was changed.

## Activation gates

- Complete Tracks 013–016 and link every blocking v1 criterion.
- Two independent user runs, two clean release candidates and one independent
  reproduction with equivalent reviewed outputs.
- Approved maintainer/backup roster, sustainability model and institutional host
  or bounded interim ownership.
- Multi-lane sign-off and public artefact verification before v1.0.0 tagging.
