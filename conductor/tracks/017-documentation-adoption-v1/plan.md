# Track 017 plan

## Bounded retained-reference guidance — 2026-08-31

This preparation does not activate Track 017 or consume another Track 003
analytical run. The original stable-release tasks remain pending.

- [x] Distinguish the public-foundation smoke generator from read-only
  inspection of the retained Track 003 report, tables and JSON, including
  full-checkout requirements and synthetic interpretation limits.
- [x] Verify the documented non-executing route, preserve retained output
  hashes and add documentation-contract regression tests with advisory review.
  Evidence: `tests/test_track017_retained_reference_guidance.py`, the updated
  tutorial/analyst/quickstart guides and the bounded review record.

## Bounded integrity maintenance — 2026-08-31

- [x] Reconcile registry/setup/index/task-state projections and prospective
  agent-review language under ADR-0009; add offline regression checks and
  retain historical evidence, dependency and release boundaries. Evidence:
  `docs/conductor-integrity-reconciliation-2026-08-31.md`.

> Review uses role-separated agent panels and the repository-owner disposition
> under ADR-0009. No independent or additional-person review is required.

## Release-authority preparation — 2026-08-03

- [x] Record the candidate-bound bounded owner disposition and stable-release
  receipt prerequisites. Evidence:
  `docs/release-authority-receipt-plan-2026-08-03.yml` and
  `tests/test_release_authority_receipt_plan.py`; stable release remains
  pending.

## Phase 1 — Documentation system

- [x] Complete quickstart, user, developer, methods, operator, steward and
  release guides. `[V1-DOC-01]` Evidence: `docs/guides/README.md` and
  role-based guides; methods and quickstart links point to the existing
  protocol and analyst workflow. This is documentation preparation, not
  usability evidence.
- [x] Add tested tutorials and reference workflows. Evidence: synthetic
  reference workflow coverage in `tests/test_reference.py` and
  `tests/test_cli_integration.py`; agent usability and owner reproduction
  remain separate gates.
- [x] Add accessibility, citation, licence and correction guidance. Evidence:
  `docs/documentation-guidance-017.md`; agent accessibility challenge is
  recorded without claiming human conformance.
- [x] Verify all public examples and links automatically. Evidence:
  `uv run python scripts/check_markdown_links.py` passed on 2026-08-01;
  command execution remains subject to full validation.

The synthetic reference workflow is exercised by `tests/test_reference.py`,
`tests/test_cli_integration.py` and the installed-package check; this is
repository-owned structural assurance only and does not close the owner-operated
reproduction or stable-release gates.

## Phase 2 — Agent usability and owner-operated reproduction

- [x] Run two role-separated usability-agent assessments of the reference
  workflow. Evidence:
  `manifests/release/track-017-bounded-exercises-2026-08-16.json`; the first
  assessment found and verified remediation of the documented bare-`python`
  failure.
- [x] Complete a separately executed owner-operated node/analyst run. Evidence:
  the same bounded receipt; explicitly non-independent.
- [x] Build two clean release candidates from locked environments. Evidence:
  exact candidate, check-log and output-manifest hashes in the bounded receipt.
- [x] Complete one owner-operated clean-environment reproduction with
  equivalent reviewed outputs. Evidence: identical output-manifest and
  verifier hashes in the bounded receipt.

## Phase 3 — Sustainability and ownership

- [ ] Publish the sole-owner maintainer, review and incident-accountability
  statement plus fail-closed incapacity and succession procedures.
- [ ] Approve contribution, succession, deprecation and support processes.
- [ ] Approve costed infrastructure and release operating model.
- [x] Confirm bounded interim single-owner ownership for the non-production
  candidate, explicitly retaining the single-point-of-failure limitation.
  Evidence: `docs/track-017-single-owner-continuity-disposition-2026-08-20.yml`.

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

## Review fixes — 2026-08-01

- [x] Add explicit quickstart and methods guides so the role-based
  documentation claim is directly navigable. Evidence:
  `docs/guides/quickstart.md` and `docs/guides/methods.md`; full
  `uv run make check` passed.

## Preparation refresh — 2026-08-01

- [x] Prepare `docs/track-017-v1-closeout-packet.md` mapping agent-panel
  usability, reproduction, ownership, governance and release receipts to the
  stable-v1 decision.
- [x] Document the clean-build and verification recipe for future release
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
- [x] Add a strict release-candidate receipt schema and synthetic
  non-authorizing fixture in `schemas/release-candidate-receipt.schema.json`
  and `tests/test_release_candidate_receipt.py`.
- [x] Add a blank ownership/sustainability packet with pending acceptance in
  `schemas/ownership-sustainability-packet.schema.json` and
  `tests/test_ownership_sustainability_packet.py`.
- [ ] Freeze and reproduce two clean release candidates from locked
  environments.
- [ ] Obtain two agent usability reports and one owner-operated
  reproduction/equivalence report.
- [ ] Record sole-owner accountability, fail-closed succession, support
  boundaries and approved sustainability costs.
- [x] Assemble the complete v1 evidence index without treating indexing as
  stable acceptance. Evidence:
  `manifests/release/v1-evidence-index-2026-08-16.json`,
  `scripts/check_v1_evidence_index.py` and `tests/test_v1_evidence_index.py`.
- [ ] Complete the remaining stable-release gates: a new exact-candidate
  sole-owner continuity-risk decision and
  public stable-artifact publication/verification after a separate stable
  release decision. Backup continuity is non-applicable to the current bounded
  non-production candidate, not satisfied.
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
- [x] Execute and validate bounded usability/build/reproduction exercises,
  apply the high-severity documentation remediation, and retain
  non-independent and non-stable claim boundaries. Evidence:
  `scripts/check_track017_bounded_exercises.py` and
  `tests/test_track017_bounded_exercises.py`.
- [x] Bind the exact merged Track 016 evidence artifact and merge commit before
  integrating this bounded preparation. Evidence: PR #104 merge
  `18910840fee787bbe2ae7d7eff40b944539a11f4` and SHA-256
  `a12ffd69c9b67e9999b9f6cbf4263387315ac67109cf1c0d6e1af793344bc8f3`.

## Evidence-contract reconciliation — 2026-08-20

- [x] Restore the append-only Track 017 plan and review evidence lost when a
  stale five-completion draft replaced the 24-completion plan, retain the
  ADR-0009 single-owner language, and add regression coverage. Evidence:
  `docs/track-017-evidence-contract-reconciliation-2026-08-20.md` and
  `tests/test_track017_evidence_contract.py`; Track 017 remains Planned and
  stable release remains disabled.
