# Synthetic reference workflow tutorial

This tutorial is an offline, synthetic smoke path for a clean checkout. It is
designed to be copied by an analyst or operator without access to controlled
data.

1. Create a clean environment with `uv sync --frozen --extra dev`.
2. Run `uv run make check` and retain the exit status.
3. Generate the deterministic public-foundation fixture using the `uv run
   python` command in [the analyst guide](guides/analyst.md).
4. Run `verify-reference-release` against the generated package.
5. Compare the verifier report and recorded hashes with the
   [release-candidate checklist](v1-release-candidate-checklist-017.md).

Start inspection with `release-manifest.json`,
`reproducibility-assessment.json`,
`analysis/expected-population-synthetic.json`, and
`reports/public-data-gap-map.md`. The full package contains hundreds of files;
these four establish identity, limitations, a synthetic output and its gap
report without requiring a user to browse the whole tree.

Expected result: validation succeeds and the package is structurally closed.
This does not establish empirical validity, independent reproduction,
controlled-data approval, or a support obligation.

If `uv` or a supported Python is unavailable, stop and resolve the prerequisite.
If `uv sync --frozen` reports a lock mismatch, do not regenerate the lock as a
workaround. If verification fails, preserve the failure report and do not use
the generated directory as a candidate.
