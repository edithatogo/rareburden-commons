# Track 017 dependency review — Documentation, adoption and stable v1

**Review date:** 2026-07-29  
**Decision:** Bounded repository preparation; stable release not activated

## Findings

- Tracks 013–016 are incomplete, so the v1 evidence index cannot be closed.
- No executed usability-agent reports, owner-operated clean reproduction,
  complete continuity/cost model or exact-candidate release disposition exists.
- Tagging v1 or making a support promise now would violate the release contract.

## Local preparation

`docs/v1-adoption-017-reference.md` defines role-based documentation coverage,
release-evidence lanes and the clean-reproduction checklist. It is preparatory
and does not imply usability, support, institutional hosting or release approval.

The repository-owned documentation slice is now present in `docs/guides/`, with
an offline synthetic reference tutorial at `docs/tutorial-reference-workflow.md`
and accessibility, citation, licence and correction guidance at
`docs/documentation-guidance-017.md`. The markdown-link check and full local
validation pass; these results do not substitute for executed agent usability,
owner-operated reproduction or an exact owner disposition.

## Review fixes — 2026-08-01

The initial review found that “quickstart” and “methods” were only indirect
links. Explicit navigable guides were added at `docs/guides/quickstart.md` and
`docs/guides/methods.md`; runtime assets were regenerated and the full check
passed with 429 tests. No external-gate claim was changed.

## Activation gates

- Complete Tracks 013–016 and link every blocking v1 criterion.
- Two role-separated usability-agent reports, two clean release candidates and
  one separately recorded owner-operated reproduction with equivalent outputs.
- Approved maintainer/backup roster, sustainability model and institutional host
  or bounded interim ownership.
- Multi-lane sign-off and public artefact verification before v1.0.0 tagging.

### Implementation checkpoint — 2026-08-01

The repository-owned preparation now records role-based guide coverage,
release-evidence lanes and a reproducible clean-environment checklist. The
full local validation suite, including documentation links, schema, safety and
synthetic reference checks, passes. These checks do not establish independent
usability, institutional ownership, cost approval, or release authorization.

Track 017 remains **Planned**. Tracks 013–016 and the independent-user,
independent-reproduction, ownership, sustainability, multi-lane review and
publication gates remain unresolved; stable v1 must not be tagged or claimed.

### Review rerun — 2026-08-01

The adoption scaffold was reviewed against the full Track 017 specification and
the blocking v1 criteria. The role map, evidence lanes and reproducibility
checklist are internally consistent, and the local documentation, schema,
safety and synthetic-reference checks pass. No repository-owned defect was
identified in this preparatory slice.

The remaining findings are substantive release gates: complete role guides and
tutorials, accessibility and external usability review, independent operator
and reproduction receipts, clean release candidates, named primary/backup
owners, approved sustainability and institutional-host decisions, all
multi-lane sign-offs, and public artefact verification. Dependencies 013–016
are not complete. Track 017 remains **Planned** and is not archive-eligible;
stable v1 must not be tagged or represented as released.

The versioned register at `docs/v1-release-evidence-register-017.md` now makes
the remaining evidence lanes, owners and bounded contingencies explicit. It
does not alter the Planned disposition or authorize publication.
