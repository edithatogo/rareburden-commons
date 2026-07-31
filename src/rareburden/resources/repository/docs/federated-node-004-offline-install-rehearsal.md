# Track 004 candidate offline-install rehearsal

**Run date:** 2026-07-31

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
are not committed. Python 3.11/3.12/3.13 Linux, Windows/WSL and other supported
platforms require their own locked wheels and receipts. A second person must
perform the documented run independently before the second-operator gate can
close. Dependency approval, signing, custodian installation and controlled-data
authorization also remain external.
