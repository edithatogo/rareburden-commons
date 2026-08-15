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

- [x] Prepared `docs/track-017-v1-closeout-packet.md` mapping agent-panel
  usability, reproduction, ownership, governance and release receipts to the
  stable-v1 decision.
- [x] Documented the clean-build and verification recipe for future release
  candidates in `docs/v1-release-candidate-checklist-017.md`; actual duplicate
  candidate builds remain open pending locked-environment execution.
- [ ] Keep v1.0.0 tagging, stable-release claims and support promises disabled
  until every accountable lane is dispositioned.

## Implementation planning — 2026-08-02

- [x] Add the dependency-ordered usability-agent, owner reproduction,
  ownership and stable-release plan with options, contingencies and
  recommendation in `docs/track-017-v1-implementation-plan-2026-08-02.md`.
- [x] Retain the legacy receipt template filename for compatibility while the
  current ADR-0009 contract uses advisory usability-agent reports and
  owner-operated reproduction; no unavailable authority is inferred.
- [x] Add a strict release-candidate receipt schema and synthetic non-authorizing
  fixture in `schemas/release-candidate-receipt.schema.json` and
  `tests/test_release_candidate_receipt.py`.
- [x] Add a blank ownership/sustainability packet with pending acceptance in
  `schemas/ownership-sustainability-packet.schema.json` and
  `tests/test_ownership_sustainability_packet.py`.
- [ ] Freeze and reproduce two clean release candidates from locked
  environments.
- [ ] Obtain two agent usability reports and one owner-operated
  reproduction/equivalence report.
- [ ] Record primary/backup ownership, succession, support boundaries and
  approved sustainability costs.
- [ ] Assemble the v1 evidence index and complete accountable release gates.
- [ ] Verify public artefacts only after a release-authority decision.

## Bounded readiness reconciliation — 2026-08-16

- [x] Record the single-owner, advisory agent-panel claim boundary and exact
  owner/backup role status. Evidence:
  `docs/track-017-bounded-readiness-reconciliation-2026-08-16.md` and
  `manifests/release/track-017-bounded-readiness-2026-08-16.json`.
- [x] Define usability-agent and owner-operated clean-reproduction preparation
  without claiming execution, independence or stable-release authority.
- [x] Add deterministic evidence-hash checks and negative tests for authority,
  continuity, dependency and stable-release overclaims. Evidence:
  `scripts/check_track017_bounded_readiness.py` and
  `tests/test_track017_bounded_readiness.py`.
- [x] Execute and validate bounded usability/build/reproduction exercises, apply
  the high-severity documentation remediation, and retain non-independent and
  non-stable claim boundaries. Evidence:
  `scripts/check_track017_bounded_exercises.py` and
  `tests/test_track017_bounded_exercises.py`.
- [x] Bind the exact merged Track 016 evidence artifact and merge commit before
  integrating this bounded preparation. Evidence: PR #104 merge
  `18910840fee787bbe2ae7d7eff40b944539a11f4` and SHA-256
  `a12ffd69c9b67e9999b9f6cbf4263387315ac67109cf1c0d6e1af793344bc8f3`.
