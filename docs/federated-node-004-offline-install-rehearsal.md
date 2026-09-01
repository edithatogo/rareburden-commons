# Track 004 candidate offline-install rehearsal

**Run date:** 2026-07-31 (historical rehearsal, not evidence for a later candidate)

**Scope:** local engineering rehearsal on macOS arm64 with Python 3.13

**Status:** passed; not an independent operator run or approved deployment

The hash-pinned production requirements were staged with:

```sh
python -m pip download --require-hashes --only-binary=:all: \
  --dest dist/wheelhouse --requirement requirements.txt
```

Seven dependency wheels were selected for the current interpreter and platform.
`scripts/check_offline_node_install.py` then created a clean environment, set
`UV_OFFLINE=1` and `PIP_NO_INDEX=1`, installed the project and dependencies using
only `--no-index --find-links`, ran `uv pip check`, executed the installed
synthetic node from an unrelated directory and verified its output fingerprint.

The rehearsal receipt recorded:

- project wheel: `rareburden-0.3.0rc2-py3-none-any.whl`;
- dependency wheel count: 7;
- installed rows: 1;
- output fingerprint:
  `sha256:32900dea79c7e5dc1fc60db255ac55106ca17a6b5d831e38c7201a1c08080e64`;
- network-disabled package commands: true.

The project wheel and seven dependencies were also assembled into
`rareburden-node-complete-candidate.zip`; the canonical eight-artifact manifest
and every embedded wheel passed `scripts/build_node_bundle.py check`.

This evidence establishes a candidate offline dependency closure only for the
recorded platform. The wheelhouse and bundle are generated build artefacts and
are not committed. Python 3.12/3.13/3.14 Linux, Windows/WSL and other supported
platforms require their own locked wheels and receipts. The historical
second-person gate requirement is superseded for prospective repository review
by ADR-0009; the original rehearsal facts above are unchanged.

## Current reproduction and interpretation

Use the [operator guide](federated-node-004-operator-guide.md) for the current
sequence. Keep the project wheel outside the dependency-only wheelhouse and
preinstall Python and `uv` before the measured offline phase. The pip download
above is network-permitted preparation, not offline-install evidence.
Network-disabled package commands do not demonstrate OS-level isolation.

The current Track 004 specification requires a separately recorded owner-operated
clean-environment installation from documentation, advisory agent-panel
challenge and owner disposition. No second person or independence is claimed
or required by that repository gate. Retain exact candidate, artifact hashes,
actual platform/runtime, command, exit status and receipt for that separate run.
This documentation refresh does not claim a new execution. Dependency approval,
release attestation, custodian installation and controlled-data authorization
remain separate evidence-bound decisions.

A later, separately executed fixed-candidate rehearsal is retained in
[the 2026-08-31 assurance record](track-004-synthetic-assurance-2026-08-31.md).
It does not alter the historical observations above or close production gates.

## Selected orchestration candidate notice — 2026-09-01

The owner selected the bounded experimental synthetic orchestration route. That
selection and its implementation do not transfer this historical installation
receipt to the changed candidate. This page records no execution of
`run_reserved_synthetic_analysis`, no reservation receipt and no result envelope.
A new installation/run claim requires a separately executed rehearsal bound to
the exact orchestration commit/tree, project and dependency wheel hashes,
platform/runtime and retained receipt.

The changed candidate remains synthetic-only. All six original Track 004 gates
remain pending and the track remains blocked; no production common-analysis
contract, authoritative custodian store, controlled-data activation, independent
operation, signed delivery or node-alpha release is inferred from the historical
or later synthetic rehearsals.
