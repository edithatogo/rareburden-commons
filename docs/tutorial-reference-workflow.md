# Synthetic reference workflow tutorial

This tutorial is an offline, synthetic smoke path for a clean checkout. It is
designed to be copied by an analyst or operator without access to controlled
data.

1. Create a clean environment with `uv sync --frozen --extra dev`.
2. Run `uv run make check` and retain the exit status.
3. Generate the deterministic public-foundation fixture using the command in
   [the analyst guide](guides/analyst.md).
4. Run `verify-reference-release` against the generated package.
5. Compare the verifier report and recorded hashes with the release-candidate
   checklist.

Expected result: validation succeeds and the package is structurally closed.
This does not establish empirical validity, independent reproduction,
controlled-data approval, or a support obligation.
