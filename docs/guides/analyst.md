# Analyst and researcher guide

Start with the [public-data-first protocol](../protocols/public-data-foundation.md),
the [methods and requirements traceability](../requirements-traceability.md),
and the [testing strategy](../testing-strategy.md).

From a clean checkout, run the locked synthetic reference workflow:

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
