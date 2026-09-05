# Track 016 implementation decision

Purpose: record the agent's bounded implementation position for the remaining
Track 016 plan tasks, and document which items must remain owner/independent/
production decisions rather than autonomous-agent closures.

**Status:** proposed; owner disposition required.
**Starting repository commit:** `a6b05f18c637406d838788e8dd2c89c7a827ed73`
(head of `track/005-economic-completion`; Track 016's `main` branch is at the
same `main` HEAD via `origin/main`).
**Scope:** reversible bounded preparation and cross-cutting security
engineering only. No production, hosted, controlled-data or stable-release
claim is made by this document.

## Bounded preparation already machine-verified

The following Track 016 evidence is present and machine-checked:

- threat model and supported runtime matrix (`docs/security-operations-016-reference.md`, `docs/supported-environments.md`);
- locked release dependencies, exact reproducible wheel/sdist builds and
  installed-wheel checks (`uv.lock`, `scripts/check_lockfile.py`,
  `scripts/build_distributions.py`, `scripts/check_built_package.py`,
  `scripts/check_installed_package.py`);
- secret, dependency, licence and static security scanning (`scripts/check_repository_safety.py`,
  CodeQL/dependency-review/Scorecard/push-protection workflows,
  `scripts/check_requirements_exports.py`);
- SBOM, checksums, OIDC keyless attestation and offline verifier
  (`scripts/build_sbom.py`, `scripts/verify_release_attestation.py`);
- privacy-safe log redaction and negative tests (`tests/test_node.py`,
  `tests/test_acquisition_security.py`);
- bounded operational metric primitive and retention/access policy
  (`rareburden.operations`, `tests/test_operations_metrics.py`,
  `docs/track-016-retention-access-policy.md`);
- owner-operated backup, restore and rollback rehearsal
  (`docs/track-016-owner-operated-exercise-receipt-2026-08-16.json`,
  `manifests/operations/track-016-bounded-operations-2026-08-16.json`);
- bounded synthetic recovery/security checklist and rehearsal
  (`docs/track-016-synthetic-recovery-security-checklist.yml`,
  `docs/track-016-synthetic-rehearsal-receipt-2026-08-05.yml`);
- exact-candidate owner disposition binding PR #165's commit and tree for 30
  days (`docs/decisions/2026-08-21-track-016-owner-exact-candidate-disposition.md`);
- fail-closed production/release readiness envelope
  (`docs/track-016-production-release-readiness-2026-08-21.yml`,
  `scripts/check_track_016_production_release_readiness.py`,
  `tests/test_track_016_production_release_readiness.py`).

The current machine checks confirm the bounded preparation:

```text
$ uv run make track-016-production-release-readiness-check
Track 016 preparation passed; handoff, production, independent review and release remain gated.
```

```text
$ uv run python scripts/check_track016_bounded_operations.py \
    manifests/operations/track-016-bounded-operations-2026-08-16.json
{"candidate_commit": "abcf10813d9ad1dd88d8fac402622f65077558d4",
 "candidate_git_object_verified": true,
 "evidence_count": 5,
 "independent_evidence": false,
 "pending_gate_count": 5,
 "status": "bounded_operations_evidence_valid"}
```

The 30 Track 016 tests pass:

```text
tests/test_track_016_production_release_readiness.py ........... [33%]
tests/test_track_016_qualifying_matrix.py ..                      [40%]
tests/test_track_016_synthetic_checklist.py ..                    [46%]
tests/test_track_016_synthetic_rehearsal_receipt.py .             [50%]
tests/test_track016_bounded_reconciliation.py ...............     [100%]
30 passed.
```

## Remaining unchecked plan tasks

Three plan tasks remain unchecked in `conductor/tracks/016-security-reliability-operations/plan.md`.

### Item 1 — qualifying owner-operated reproduction and agent-panel security challenge

> *Obtain qualifying owner-operated reproduction and agent-panel security
> challenge receipts against the same exact candidate, with owner disposition;
> no independent review is claimed.*

This requires receipts **independent of the repository owner and the agent
panel** (per `docs/track-016-qualifying-evidence-matrix-2026-08-03.yml`,
`docs/decisions/ADR-0011-single-accountable-human-enforcement.md` and the
review-gate definition in `conductor/workflow.md`). An autonomous agent cannot
create independent review by relabelling owner-operated work. The bounded
preparation above is the agent's truthful position; this item remains a
named-independent-reviewer-or-equivalent gate.

### Item 2 — qualifying production operations after Tracks 004 and 014

> *Exercise qualifying production operations after Tracks 004 and 014 are
> complete and record the production-environment receipt.*

This item is **dependency-gated**. Tracks 004 (federated-node-runner) and 014
(atlas-api-release) are not Complete in `conductor/tracks.md`. The track
metadata lists both as dependencies. The agent cannot legitimately exercise
production operations before dependency satisfaction, and ADR-0011 keeps
production disabled by default.

### Item 3 — owner exact-candidate release decision

> *Record the owner's exact-candidate release decision after all qualifying
> gates are satisfied.*

This is explicitly the repository owner's decision per the single-accountable-
human model. The owner disposition already on file
(`docs/decisions/2026-08-21-track-016-owner-exact-candidate-disposition.md`)
covers bounded preparation only and explicitly does not constitute release
authority. The release decision cannot be moved by an agent.

## Recommendation

1. Keep the track's `planned` status in `conductor/tracks.md` and
   `conductor/tracks/016-security-reliability-operations/metadata.json`.
   The bounded preparation is complete but the production, independent-review,
   backup-handoff and release-authority gates remain pending.
2. Reaffirm that the agent's bounded work is documented above and remains
   machine-checked by `track-016-production-release-readiness-check`,
   `check_track016_bounded_operations.py`, and the Track 016 test module.
3. Record any new bounded preparation only when it can be produced from
   repository-owned, non-independent evidence; do not promote agent work to
   independent review, production approval or release authority.
4. The next safe autonomous task is a Track 016 audit that records:
   - that the bounded evidence above is still valid against the current
     `main` HEAD;
   - that the machine-checked state in
     `docs/track-016-production-release-readiness-2026-08-21.yml` still has the
     five pending gates (`backup_owner_handoff`, `independent_operator`,
     `independent_security`, `release_authority`, `production_operations`);
   - that no production, hosted, controlled-data, partnership or stable-release
     claim is made.
   This is owner-prepared evidence and not a substitute for the items above.

## Non-claims and stop conditions

This decision document:

- does not claim Track 016 is Complete, Active, Ready or Blocked;
- does not claim independent operator, independent security, completed backup
  handoff, production operations, controlled-data, hosted or stable-release
  authority;
- does not invent a backup owner; ADR-0011 supersedes the private backup
  proposal with fail-closed owner-incapacity, credential-compromise and
  recovery controls;
- does not promote owner-operated or agent-panel evidence to independent
  evidence by relabelling;
- must be invalidated by any critical or high-severity finding, evidence hash
  drift, sensitive-value exposure, restore or rollback failure, resource-
  budget breach, owner-capacity loss or material qualifying-review finding.

## Advisory assessment

These are simulated perspectives, not sub-agents, independent reviewers or
human consensus.

- Engineering/security: bounded preparation is machine-checked and the
  readiness envelope fail-closes on the remaining gates. Continuing to add
  repository-owned preparation does not close independent or production gates.
- Programme/release: dependency on Tracks 004/014 completion plus owner
  release decision are real and unavoidable. Marking Track 016 Ready or
  Active without them would misrepresent the state.
- Continuity: ADR-0011's fail-closed recovery posture is the correct answer
  when no backup owner can be honestly named; do not weaken it for convenience.

No dissenting human assessment has been collected; no human consensus is
claimed.