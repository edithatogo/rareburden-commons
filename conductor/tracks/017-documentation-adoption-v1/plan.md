# Track 017 plan

> Repository-owned review uses the subagent panel under ADR-0008; independent usability, operational ownership and release authority remain separate.

## Phase 1 — Documentation system

- [x] Complete quickstart, user, developer, methods, operator, steward and release guides. `[V1-DOC-01]` Evidence: `docs/guides/README.md` and role-based guides; methods and quickstart links point to the existing protocol and analyst workflow. This is documentation preparation, not usability evidence.
- [x] Add tested tutorials and reference workflows. Evidence: synthetic
  reference workflow coverage in `tests/test_reference.py` and
  `tests/test_cli_integration.py`; independent usability and reproduction
  remain separate gates.
- [x] Add accessibility, citation, licence and correction guidance. Evidence: `docs/documentation-guidance-017.md`; external accessibility review remains open.
- [x] Verify all public examples and links automatically. Evidence: `uv run python scripts/check_markdown_links.py` passed on 2026-08-01; command execution remains subject to full validation.

The synthetic reference workflow is exercised by `tests/test_reference.py`,
`tests/test_cli_integration.py` and the installed-package check; this is
repository-owned structural assurance only and does not close independent-user
usability or reproduction gates.

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

## Review fixes — 2026-08-01

- [x] Add explicit quickstart and methods guides so the role-based
  documentation claim is directly navigable. Evidence: `docs/guides/quickstart.md`
  and `docs/guides/methods.md`; full `uv run make check` passed.

## Preparation refresh — 2026-08-01

- [x] Prepared `docs/track-017-v1-closeout-packet.md` mapping independent
  usability, reproduction, ownership, governance and release receipts to the
  stable-v1 decision.
- [x] Documented the clean-build and verification recipe for future release
  candidates in `docs/v1-release-candidate-checklist-017.md`; actual duplicate
  candidate builds remain open pending locked-environment execution.
- [ ] Keep v1.0.0 tagging, stable-release claims and support promises disabled
  until every accountable lane is dispositioned.
