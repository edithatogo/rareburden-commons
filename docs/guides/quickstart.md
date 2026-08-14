# Quickstart

This is the shortest safe path through the synthetic reference workflow. It
requires no credentials or controlled data.

```bash
uv sync --frozen --extra dev
uv run make check
```

Then follow the [reference workflow tutorial](../tutorial-reference-workflow.md).
The generated package is synthetic and demonstrates structural and
deterministic checks only; it is not an empirical estimate or a production
deployment.
