# Track 017 plan

## Release-authority preparation — 2026-08-03

- [x] Record the candidate-bound bounded owner disposition and stable-release
  receipt prerequisites. Evidence:
  `docs/release-authority-receipt-plan-2026-08-03.yml` and
  `tests/test_release_authority_receipt_plan.py`; stable release remains
  pending.

> Review uses role-separated agent panels and the repository-owner disposition
> under ADR-0009. No independent or additional-person review is required.

## Phase 1 — Documentation system

- [x] Complete quickstart, user, developer, methods, operator, steward and release guides. `[V1-DOC-01]` Evidence: `docs/guides/README.md` and role-based guides; methods and quickstart links point to the existing protocol and analyst workflow. This is documentation preparation, not usability evidence.
- [x] Add tested tutorials and reference workflows. Evidence: synthetic
  reference workflow coverage in `tests/test_reference.py` and
  `tests/test_cli_integration.py`; agent usability and owner reproduction
  remain separate gates.
- [x] Add accessibility, citation, licence and correction guidance. Evidence: `docs/documentation-guidance-017.md`; external accessibility review remains open.
- [x] Verify all public examples and links automatically. Evidence: `uv run python scripts/check_markdown_links.py` passed on 2026-08-01; command execution remains subject to full validation.

The synthetic reference workflow is exercised by `tests/test_reference.py`,
`tests/test_cli_integration.py` and the installed-package check; this is
repository-owned structural assurance only and does not close the usability or
owner-operated reproduction gates.

## Phase 2 — Agent usability and owner-operated reproduction

- [x] Run two role-separated usability-agent assessments of the reference workflow. Evidence: `manifests/release/track-017-bounded-exercises-2026-08-16.json`; the first assessment found and verified remediation of the documented bare-`python` failure.
- [x] Complete a separately executed owner-operated node/analyst run. Evidence: same bounded receipt; explicitly non-independent.
- [x] Build two clean release candidates from locked environments. Evidence: exact candidate, check-log and output-manifest hashes in the bounded receipt.
- [x] Complete one owner-operated clean-environment reproduction with equivalent reviewed outputs. Evidence: identical output-manifest and verifier hashes in the bounded receipt.

## Phase 3 — Sustainability and ownership

- [ ] Publish maintainer, reviewer, incident and backup-owner roster.
- [ ] Approve contribution, succession, deprecation and support processes.
- [ ] Approve costed infrastructure and release operating model.
- [ ] Confirm institutional host or bounded interim ownership.

## Phase 4 — Stable release review

- [ ] Assemble evidence for every blocking v1 criterion.
- [ ] Remove unsupported capabilities or close remaining gaps.
- [ ] Complete agent-panel methods, community/harm, rights/data-use,
  engineering, security and programme recommendations and owner disposition.
- [x] Record an exact-candidate bounded synthetic/public-preview owner decision
  with stable release deferred. Evidence: immutable issue #16 comment
  `5303792002` and
  `manifests/release/track-017-owner-bounded-disposition-2026-08-16.json`.
- [ ] Record a later stable release, revise or stop decision only for its exact
  candidate; the current owner decision does not authorize stable release.

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

## Preparatory release planning — 2026-08-01

- [x] Create a versioned evidence register mapping the blocking v1 criteria to
  objective evidence, current state and bounded contingencies. Evidence:
  `docs/v1-release-evidence-register-017.md`. The register is traceability
  scaffolding; it does not pass any external or independent gate.
