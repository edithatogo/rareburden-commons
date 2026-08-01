# Track 017 plan

## Phase 1 — Documentation system

- [ ] Complete quickstart, user, developer, methods, operator, steward and release guides. `[V1-DOC-01]`
- [ ] Add tested tutorials and reference workflows.
- [ ] Add accessibility, citation, licence and correction guidance.
- [ ] Verify all public examples and links automatically.

## Phase 2 — External use and reproduction

- [ ] Recruit two independent users for reference-workflow usability testing.
- [ ] Complete independent node-operator or analyst run.
- [ ] Build two clean release candidates from locked environments.
- [ ] Complete one independent reproduction with equivalent reviewed outputs.

## Phase 3 — Sustainability and ownership

- [ ] Publish maintainer, reviewer, incident and backup-owner roster.
- [ ] Approve contribution, succession, deprecation and support processes.
- [ ] Approve costed infrastructure and release operating model.
- [ ] Confirm institutional host or bounded interim ownership.

## Phase 4 — Stable release review

- [ ] Assemble evidence for every blocking v1 criterion.
- [ ] Remove unsupported capabilities or close remaining gaps.
- [ ] Complete scientific, patient/community, data-governance, engineering, security and programme sign-off.
- [ ] Record final release, bounded exclusion, revise or stop decision.

## Phase 5 — Publish and verify

- [ ] Finalise changelog, migration guide, release notes and scope statement.
- [ ] Build source, Git, data-package and provenance-rich release artefacts.
- [ ] Tag v1.0.0 and archive immutable artefacts only after approval.
- [ ] Verify published artefacts using public instructions and record the result.

## Preparatory dependency review — 2026-07-29

- [x] Define role-based documentation coverage, release-evidence lanes and clean
  reproduction checklist without activating v1 publication. Evidence:
  `docs/v1-adoption-017-reference.md` and review record.

## Preparatory implementation — 2026-08-01

- [x] Record role-based documentation coverage, evidence-lane dispositions and
  the exact clean-reproduction steps. Evidence:
  `docs/v1-adoption-017-reference.md`. This is a release-evidence scaffold,
  not independent usability or v1 evidence.
- [x] Run the repository documentation, schema, safety and reference-workflow
  checks as the current executable documentation baseline. Evidence:
  `uv run make check`; independent users, support owners and release approval
  remain open.
