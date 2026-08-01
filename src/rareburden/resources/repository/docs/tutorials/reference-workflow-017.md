# Synthetic reference workflow tutorial

This is a maintainer-tested, offline workflow over synthetic fixtures. It is
not an empirical estimate, independent reproduction, or controlled-data
authorization.

## Run

```bash
uv sync --frozen --extra dev
PYTHONPATH=src:. python -m rareburden demo-public-foundation \
  --root . --output outputs/public-foundation-synthetic \
  --created-at 2026-07-27T00:00:00Z --overwrite
```

Inspect the machine-readable and human-readable gap products:

```bash
python -m json.tool outputs/public-foundation-synthetic/reports/public-data-gap-map.json >/dev/null
sed -n '1,80p' outputs/public-foundation-synthetic/reports/public-data-gap-map.md
uv run make check
```

Only synthetic/public reference materials belong in this workflow. Do not add
participant-level, controlled, small-cell or licence-restricted data. Follow
the release policy for correction, withdrawal and governance decisions. A
maintainer-only run does not satisfy the independent-user gate.
