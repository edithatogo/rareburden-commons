# Analyst and researcher guide

Start with the [public-data-first protocol](../protocols/public-data-foundation.md),
the [methods and requirements traceability](../requirements-traceability.md),
and the [testing strategy](../testing-strategy.md).

## Inspect retained Track 003 evidence

For read-only inspection of the published synthetic reference, use a full
repository checkout with `results/` and `manifests/`. These resources are not
included in the installed-wheel documentation projection. From its root:

```bash
uv sync --frozen --extra dev
uv run python -m scripts.check_track003_reference_closeout --root .
```

The verifier reads retained evidence without executing analysis or generating
outputs. A pass confirms integrity of the existing historical package and
receipts, not new analytical-run authorization or empirical validity. On missing
files or hash mismatch, stop and preserve the failure; do not regenerate outputs
or edit historical receipts to force agreement.

Follow the [inspection tutorial](../tutorial-reference-workflow.md) for the three
files under `results/track-003-reference-2026-08-31/`, and the
[acceptance record](../track-003-reference-closeout-2026-08-31.md) for provenance
and scope. Inputs and conditional uncertainty are invented, costs use fictional
currency, unavailable values are not zero, and same-host reproduction is not
independent validation. The report is not an empirical estimate or clinical-use
product.

## Generate the public-foundation smoke fixture

From a clean checkout, run the locked synthetic reference workflow below. This
creates a different package from the retained Track 003 reference. It is not a
command for rerunning Track 003:

```bash
uv sync --frozen --extra dev
uv run make check
PYTHONPATH=src:. uv run python -m rareburden demo-public-foundation \
  --root . --output outputs/public-foundation-synthetic \
  --created-at 2026-07-27T00:00:00Z --overwrite
PYTHONPATH=src:. uv run python -m rareburden verify-reference-release \
  --root . --release outputs/public-foundation-synthetic \
  --verified-at 2026-07-27T00:00:00Z
```

Record the commit, environment, command transcript and output hashes. Treat
the result as synthetic structural/deterministic assurance, not empirical
validation or independent reproduction.
