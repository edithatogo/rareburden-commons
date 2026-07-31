# Codex autonomous continuation contract

You are taking over **RareBurden Commons**, the technical infrastructure for the proposed Global Rare Disease Burden Initiative.

Operate autonomously. Do not ask for confirmation for routine engineering, documentation, Git or GitHub actions. Use evidence and the existing repository context to make conservative decisions. Where a genuinely external dependency is unavailable, record the blocker precisely, create or update the corresponding issue/track evidence, and continue all feasible work.

## 1. Non-negotiable safety and truthfulness

1. Preserve all existing local and remote work. Never delete an unrelated repository, branch, tag, worktree, issue, project or release.
2. Never force-push a shared branch. Never rewrite released `v0.1.0` or `v0.2.0` history.
3. Never commit the outer handoff ZIP, credentials, tokens, private configuration, patient-level records, row-level controlled data, small cells or other sensitive health information.
4. Treat every empirical-looking example in the current branch as synthetic unless a source record proves otherwise.
5. Do not claim partnership, endorsement, data access, preregistration, independent reproduction, external replication, peer review, custodian approval or constituted governance without documentary evidence.
6. Do not mark a Conductor track complete merely because code or documentation exists. Completion requires every required task, objective evidence, applicable tests and `review.md`.
7. Preserve exact provenance: source/version, retrieval/acquisition event, licence state, transformation, software/environment identity, analytic decisions, uncertainty and limitations.
8. Do not automate around click-through terms, access controls, robots restrictions, rate limits or controlled-research agreements. Use manual registration when automation is not clearly permitted.
9. Keep the public-data-first and federated design: **link estimates, not identities**.
10. A green synthetic reference release proves internal auditability, not empirical validity.

## 2. Establish repository truth before changing anything

Read, in order:

1. `AGENTS.md`
2. `README.md`
3. `docs/handoff/implementation-status.md`
4. `conductor/index.md`
5. `conductor/product.md`
6. `conductor/product-guidelines.md`
7. `conductor/tech-stack.md`
8. `conductor/workflow.md`
9. `conductor/roadmap.yml`
10. `docs/roadmap-v1.md`
11. `docs/v1-acceptance-criteria.md`
12. `docs/requirements-traceability.md`
13. active/in-review track specifications, plans, metadata and reviews.

Then inspect:

```bash
git status --short --branch
git log --oneline --decorate --graph --all --max-count=80
git remote -v
git tag --list --sort=version:refname
python --version
command -v uv || true
command -v gh || true
```

The authoritative handoff branch is `handoff/v0.3.0-rc.2`. The tag `handoff-v0.3.0-rc.2` is a portable handoff marker, not a final scientific release tag. The canonical final release tag remains gated as `v0.3.0`.

## 3. Restore and verify the local development environment

Prefer the exact lock:

```bash
uv sync --frozen --extra dev
uv run make check
uv run make coverage
uv run make critical-coverage
uv run make reproducibility
uv run make build
uv run make package-check
uv run make sbom
```

When network or a package index is unavailable, do not mutate the lock merely to obtain a green run. Run every offline-capable check, record the unavailable gate, and retry when access is restored.

At minimum verify:

- programme, catalogue, landscape, roadmap and all track metadata;
- all JSON Schemas;
- runtime-asset closure;
- requirements/lock drift;
- workflow security policy;
- repository safety;
- complete tests including Hypothesis property tests;
- branch-aware coverage and critical-module thresholds;
- strict type checking, lint and format checks;
- exact two-process reference reproducibility;
- deterministic wheel and source-distribution bytes;
- built-package inspection;
- installed-wheel programme validation and reference workflow from an unrelated directory;
- seven-gate independent reference-release verification.

Do not hide an order-dependent failure through test sharding. A split test run may diagnose a problem but does not replace the single-process gate.

## 4. GitHub repository creation and wiring

### Defaults

Use environment overrides when present:

```text
RAREBURDEN_GITHUB_OWNER       default: edithatogo
RAREBURDEN_GITHUB_REPO        default: rareburden-commons
RAREBURDEN_REMOTE_VISIBILITY  default: private
RAREBURDEN_GITHUB_PROJECT     default: RareBurden Commons — Roadmap to v1.0
```

First run:

```bash
gh auth status
gh auth setup-git
```

If authentication is unavailable, continue locally and create a precise handoff report listing the exact commands that remain. Do not invent a remote URL or claim a push occurred.

### Reuse before create

1. Inspect existing `origin` and any matching GitHub repository.
2. If the current remote is clearly the intended RareBurden repository, preserve it.
3. If no intended repository exists, create `${RAREBURDEN_GITHUB_OWNER:-edithatogo}/${RAREBURDEN_GITHUB_REPO:-rareburden-commons}` with `${RAREBURDEN_REMOTE_VISIBILITY:-private}`.
4. Do not overwrite a remote with unrelated history.
5. If a repository of that name exists with unrelated history, create an explicit issue/blocker and use a safe alternative branch or repository name rather than destroying it.

A typical creation command is:

```bash
gh repo create "${RAREBURDEN_GITHUB_OWNER:-edithatogo}/${RAREBURDEN_GITHUB_REPO:-rareburden-commons}" \
  --${RAREBURDEN_REMOTE_VISIBILITY:-private} \
  --source . \
  --remote origin \
  --description "Open, provenance-first infrastructure for measuring the collective burden of rare diseases"
```

Push without rewriting history:

```bash
git push -u origin main
git push -u origin handoff/v0.3.0-rc.2
git push origin --tags
```

The historical `v0.1.0` and `v0.2.0` tags must remain intact.

### Repository settings

Configure idempotently where permissions allow:

- issues enabled;
- wiki disabled;
- squash merge enabled;
- merge commits and rebase merge disabled unless repository policy requires otherwise;
- delete head branches after merge;
- allow update branch;
- private vulnerability reporting enabled;
- default branch `main`;
- branch/ruleset protection requiring CI, review and no force-push;
- protected release environment for attested tags/releases;
- secret scanning, push protection, Dependabot alerts/updates and CodeQL where plan/permissions allow.

Never weaken protections solely to make a push succeed.

## 5. Convert Conductor into GitHub execution controls

Treat `conductor/roadmap.yml` and each track directory as the canonical programme plan. Create or update GitHub artefacts idempotently.

### Labels

Create a compact label taxonomy, including:

- `track:<id>` for each track;
- `priority:must`, `priority:should`, `priority:could`;
- `gate:scientific`, `gate:data-governance`, `gate:patient-community`, `gate:engineering`, `gate:security`, `gate:programme`, `gate:release`;
- `status:blocked`, `status:in-review`, `external-dependency`, `controlled-data`, `reproducibility`, `provenance`, `good-first-issue` where appropriate.

### Milestones

Create milestones for `v0.3.0` through `v1.0.0` using the roadmap objectives and exit gates. Do not close a milestone until its machine-readable release gate is satisfied.

### Issues and subissues

For each unchecked Conductor task:

1. Search for an existing issue by track/task identity.
2. Reuse/update rather than duplicate.
3. Include track, requirement IDs, acceptance evidence, dependencies and review gates.
4. Use subissues or task lists to preserve track decomposition where supported.
5. Link implementation commits and review evidence.
6. Keep external-source, legal/licence and governance tasks separate from code tasks.

### GitHub Project v2

Create or reuse `${RAREBURDEN_GITHUB_PROJECT:-RareBurden Commons — Roadmap to v1.0}`. Add issues and configure fields where permissions allow:

- Release
- Track
- Status
- Priority
- Owner role
- Review gate
- V1 critical
- Evidence state

Create useful views: current release, blocked/external, scientific review, engineering/security, and roadmap to v1.

GitHub project automation must be idempotent. Query before creating.

## 6. Immediate implementation priorities

### A. Close handoff/release-engineering gaps

1. Run the complete exact locked harness, including Hypothesis, mypy and Ruff.
2. Resolve any dependency, version, runtime-asset, metadata or documentation drift.
3. Preserve the canonical deterministic sdist implementation and add regression tests for tar/gzip metadata.
4. Validate installed-wheel output-path behaviour and packaged repository discovery on Linux, macOS and Windows.
5. Exercise and harden the `verify-reference-release` CLI command across checkout, source-archive and installed-wheel contexts.
6. Produce coverage evidence and raise scientific/provenance-critical modules toward the v1 95% branch target.
7. Run hosted CodeQL, dependency review, Scorecard, vulnerability audit, SBOM and attestation workflows.
8. Verify restoration from both the Git bundle and source ZIP.

### B. Finish Track 002 without overstating access

1. Reverify live source URLs, release conventions, terms and redistribution conditions with dated evidence.
2. Record access tests separately from metadata, terms and acquisition tests.
3. Add production source descriptors and checksum/version discovery where lawful.
4. Exercise source-change, rate-limit, redirect, licence-uncertainty and manual-registration paths.
5. Obtain or record required scientific and data-governance reviews.
6. Do not automate IHME/OECD or another restricted flow until terms clearly permit it.

### C. Finish Track 007 rigorously

1. Convert the provisional landscape into a registered scoping/landscape protocol.
2. Run reproducible scholarly and repository-native searches across GitHub, Zenodo, OSF and Hugging Face.
3. Preserve queries, dates, result counts, deduplication and exclusions.
4. Obtain independent methods and patient/community challenge.
5. Reassess `proceed_with_narrowed_scope` and update the product thesis if evidence warrants narrowing, partnership or stopping.

### D. Advance v0.4 foundations where work is non-regrettable

Without declaring v0.3 complete, continue non-regrettable implementation spikes for:

- governed semantic hierarchy and mapping-review states;
- evidence conflicts and alternative parameter sets;
- structured transportability sensitivity and uncertainty inflation;
- overlap-model contracts;
- schema migrations and semantic diffs;
- synthetic federated node value allow-lists, ephemeral duplicate-detection keys, secondary suppression and repeated-query attack tests;
- monogenic-diabetes demonstrator protocol and fully synthetic reference analysis.

Keep these tied to their own Conductor tracks and do not bypass dependencies in status reporting.

## 7. Development method

For every material task:

1. Select or create the correct Conductor track/task.
2. Confirm acceptance criteria and failure behaviour before implementation.
3. Add or improve tests first when practical.
4. Implement the smallest coherent vertical slice.
5. Run focused checks, then the full applicable harness.
6. Update task checkbox, traceability and review evidence.
7. Commit with a focused message.
8. Push the branch and open/update a pull request.
9. Merge only when required gates pass.
10. Continue to the next unblocked task.

Use short-lived branches named by track/task. Prefer conventional commit messages such as:

```text
feat(acquisition): verify versioned WHO release descriptors
fix(provenance): make workflow projection insertion-order invariant
test(disclosure): add repeated-query attack scenarios
docs(track-007): register landscape search strategy
ci(release): require installed-wheel reference verification
```

Do not accumulate a giant unreviewable branch if smaller evidence-bearing commits are possible.

## 8. Autonomous stopping rules

Continue until one of these applies:

- all feasible current-release tasks are implemented and pushed;
- a task requires an unavailable external approval, credential, legal decision or controlled dataset;
- a scientific choice has multiple materially different defensible options and cannot be resolved from the protocol or evidence;
- continuing would risk data, security, history or governance integrity.

When blocked, do not simply stop. Create/update the issue, document the exact evidence required, identify a safe next task and continue there.

## 9. Final report required from Codex

At the end of the autonomous run, report only verified facts:

- local repository path;
- GitHub repository URL, or why it could not be created;
- current branch and commit;
- preserved historical tags;
- commits made and pull requests merged/opened;
- issues, milestones and project created/updated;
- exact tests/harnesses run and results;
- hosted CI/security status;
- Conductor track/status changes;
- release maturity achieved;
- remaining blockers, each linked to an issue or track task;
- the safest next autonomous task.

Do not claim background work, future completion or success that did not occur.
