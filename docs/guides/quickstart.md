# Quickstart

This is the shortest safe path to the synthetic reference workflows. They
require no credentials or controlled data. Choose either read-only inspection of
retained Track 003 evidence or generation of the separate public-foundation smoke
fixture; they are not interchangeable.

Prerequisites are Git, [`uv`](https://docs.astral.sh/uv/getting-started/installation/),
a supported Python version (3.12–3.14), and a clean repository checkout. Run
the commands from the repository root. Allow about 25 minutes, 2 GiB of free
working space and network access for the initial locked dependency sync. A `uv`
warning that hardlinks are unavailable across filesystems is harmless when it
explicitly reports that files will be copied instead.

```bash
uv sync --frozen --extra dev
uv run make check
```

Then choose a route in the [reference workflow tutorial](../tutorial-reference-workflow.md):

- Inspect Track 003's retained report, CSV and JSON and verify existing evidence
  without new analysis. This requires the full checkout's `results/` and
  `manifests/`, not an installed wheel alone. Verification does not authorise a
  new analytical run.
- Generate the existing public-foundation smoke fixture, a different package
  from the retained Track 003 results.

The generated package is synthetic and demonstrates structural and
deterministic checks only; it is not an empirical estimate or a production
deployment.

If `uv` is missing, install it using the linked official instructions. If a
lock mismatch occurs, stop rather than updating the lock implicitly. Use
`uv run python`, not a bare `python`, for the tutorial commands. A verifier
failure is fail-closed: retain its report and do not treat the output as a
candidate.
