# Quality-frontier evidence — 2026-08-15

This receipt reconciles GitHub issues 20–22 with repository and hosted evidence. It records
software assurance, not scientific, clinical, rights, patient/community or release approval.

## Testing applicability

- **Property-based testing — implemented and warranted.** Hypothesis exercises bounded burden
  arithmetic and numerical invariants in `tests/test_burden.py` and
  `tests/test_burden_numerical_assurance.py`.
- **Contract testing — implemented and warranted.** JSON Schema validation, negative fixtures,
  CLI integration tests and source-adapter contract tests exercise the repository's versioned
  file/API contracts. A network consumer/provider contract framework is not applicable because
  the supported release surface is currently an offline package and static schema set.
- **Mutation testing — implemented as a bounded scheduled lane.** Mutmut targets the
  safety/science-critical `rareburden.burden` module using its focused deterministic tests.
  It is scheduled or manually dispatched because mutation runs are too expensive for the fast
  pull-request gate. The initial floor is 65% killed mutants with zero untested, suspicious,
  timed-out, interrupted or crashing mutants; results are retained as an artifact. The local
  baseline killed 121 of 174 mutants (69.54%). Ratchet the floor as surviving mutants are
  dispositioned and tests improve.
- **DST/MT — excluded.** There is no distributed concurrent service or trained ML model in the
  bounded supported surface. Reassess if either enters release scope.

## Repository and hosted controls

- Third-party Actions are immutable-SHA pinned, checkout credentials are not persisted, jobs
  have timeouts and workflows use explicit least privilege and concurrency controls.
- CodeQL, dependency review, locked dependency audit, OpenSSF Scorecard, SBOM/provenance,
  branch-aware coverage, critical-module coverage, workflow policy, zizmor and secret scanning
  are configured. CodeQL, dependency review, CI and Scorecard have successful hosted receipts.
- Codecov uses GitHub OIDC and fails closed on upload errors. Its hosted repository/status receipt
  remains pending until this workflow revision runs.
- Renovate is the sole dependency-update bot. `renovate.json` inherits
  `github>edithatogo/renovate-config`; Dependabot configuration is intentionally absent.
- `requirements.txt` and `requirements-dev.txt` are generated exports of `uv.lock`, so
  Renovate must not update them directly. Dependency changes originate in
  `pyproject.toml` or lock-file maintenance; the repository export checks then verify
  that all three representations agree.
  A Dependency Dashboard or Renovate PR is still required as hosted proof that app access works.
  `scripts/check_renovate_readiness.py` now validates these repository-owned prerequisites
  offline and explicitly reports `hosted_app_execution_observed: false`; passing that check is
  configuration evidence only. A 2026-08-16 GitHub audit found no Renovate-authored event,
  pull request or Dependency Dashboard across the repository's visible history, so issues #21
  and #22 remain open rather than inferring app access from installation or configuration.
- The repository is solo-maintained: zero mandatory human approvals, no CODEOWNERS gate, and
  protected automated checks. Owner self-review is not represented as independent review.

## Drift and remaining hosted receipts

At audit time the GitHub API returned no active repository ruleset and no classic branch
protection for `main`; this is a hosted configuration gap, not a source-code defect. The intended
ruleset blocks deletion and force-push, requires pull requests with zero approvals, requires
stable automated checks, and retains administrator recovery. After configuration, capture its
ruleset identifier and exact required-check list here or in an issue comment.

Hosted evidence still required before closing the parent issue:

1. successful first run of workflow-security lint, secret scan, mutation testing and Codecov;
2. Codecov repository/status activation;
3. Renovate Dependency Dashboard or dependency pull request;
4. active `main` ruleset receipt with no mandatory review and owner recovery retained.
