# Local CI evidence — 2026-09-03

This packet records an owner-operated reproduction of the hosted assurance commands at commit `37465df855c1e12c65728b3158084f22b065bb24`.

## Environment

- Host: macOS arm64
- `uv`: 0.11.8
- Python: 3.13.13
- Environment: `uv sync --frozen --extra dev --python 3.13`
- Reference epoch: `1760000000`

## Results

- `uv run --python 3.13 make ci`: **pass** — 1,980 tests; 91.07% total coverage; critical coverage, reproducibility, packaging, SBOM and node checks passed.
- Portability commands were exercised in a clean-output sequence. The first run exposed a repository fixture dependency on generated coverage artifacts; the second run recorded the same expected fixture-dependent failures after `make clean`, then completed build and installed-package staging. This is not represented as a clean portability pass.
- Hosted CI remains the authoritative cross-platform result; workflow-dispatch run `33740618586` passed all platform and assurance jobs.

## Receipts

The command transcripts are preserved in `*.log`. Generated distribution hashes from the successful locked assurance build are:

| Artifact | SHA-256 |
|---|---|
| `dist/rareburden-0.3.0rc2-py3-none-any.whl` | `f00aa91a2823bba566dc0a2f2bbb7161b1444a62837b346e8a2aafe0f2ef2ee0` |
| `dist/rareburden-0.3.0rc2.tar.gz` | `f8a15016cf51d80024019dd64bc5f49dda7d99f0c9956b23e2a9188132459007` |
| `dist/offline-install-receipt.json` | `1b0714ff2e6c3acc9d0ea4a9884c1cb98ba7988ae5b4a932819fa361cdd638a2` |

This evidence is local, synthetic/repository-owned assurance only. It does not assert empirical validation, controlled-data access, independent review, publication, or release authority.
