# Synthetic reference workflow tutorial

This tutorial offers two distinct synthetic paths for a clean checkout: generate
the public-foundation smoke fixture, or inspect the already retained Track 003
reference package without rerunning its analysis. Neither requires controlled
data. Initial environment provisioning may need network access; the retained
package verifier itself reads local evidence only.

## Inspect the retained Track 003 package without new analysis

Use a full repository checkout containing `results/` and `manifests/`, not just
an installed wheel. From the repository root, provision the locked environment
with `uv sync --frozen --extra dev`, then run:

```bash
uv run python -m scripts.check_track003_reference_closeout --root .
```

Expected result: `Track 003 synthetic package and reproduction evidence passed;
no analysis executed`. This checks the retained output hashes, exact historical
source snapshot, decision and execution/reproduction receipts. It does not
generate outputs, execute the historical analysis or authorise another run.
Missing files or changed hashes are a stop condition: preserve the failure and
resolve the checkout/evidence mismatch, not regenerate the package to make the
check pass.

Read the [Track 003 acceptance and reproduction record](track-003-reference-closeout-2026-08-31.md)
for authoritative provenance, approval scope and limitations. In the full
checkout, inspect `results/track-003-reference-2026-08-31/`:

- `reference-report.md` is the human-readable scenario report.
- `reference-tables.csv` contains the tabular metrics and their interpretation
  fields; keep those labels alongside values.
- `reference-results.json` retains structured results and assumptions.

All inputs are invented. Conditional intervals describe invented parameter
uncertainty, not empirical confidence; fixed assumptions remain uncertain even
when an interval has zero width. Costs use fictional constant-2025 currency.
Unavailable burden is not zero, and overlapping outcome groups must not be
summed. The recorded separate reproduction is same-host owner-operated evidence,
not independent validation. Clinical use, country rankings, empirical validity
and production release are not established. Reading or verifying these files is
not new analytical-run authorization.

## Generate the separate public-foundation smoke fixture

This existing workflow generates a different fixture package. It does not create
or replace the retained Track 003 report, CSV or JSON.

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
