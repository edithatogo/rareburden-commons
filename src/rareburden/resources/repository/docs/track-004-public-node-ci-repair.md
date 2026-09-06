# Track 004 — Public-node dependency-review repair

## Scope and authorization

The owner explicitly authorized replacing the PyArrow dependency flagged by
PR 317 dependency review, refreshing offline evidence and merging only after
Actions pass. This scoped work changes the public-node dependency lock and
adds this evidence note. The main task owns policy/test corrections, full
checks, review, commits, hosted CI and merge. No Actions exemption, advisory
allowlist or security-check bypass is introduced.

## Advisory interpretation and dependency repair

[GHSA-rgxp-2hwp-jwgg / CVE-2026-25087](https://github.com/advisories/GHSA-rgxp-2hwp-jwgg)
lists PyArrow versions from 15.0.0 to before 23.0.1 as affected and 23.0.1 as
patched. Its technical description concerns an Arrow C++ IPC-file
pre-buffering use-after-free. It states that this API is not exposed through
Python bindings. The public-node path reads pinned Parquet snapshots through
pandas/PyArrow, not that C++ IPC pre-buffering API. This distinction limits the
exposure claim; it is not a reason to waive the dependency gate. The approved
repair upgrades to the patched release without claiming a demonstrated Python
exploit or that every possible Arrow vulnerability has been excluded.

The replacement was freshly downloaded using:

```sh
.venv/bin/python -m pip --isolated download \
  --index-url https://pypi.org/simple --no-cache-dir \
  --only-binary=:all: --no-deps \
  --dest /Volumes/PortableSSD/rbd-public-data/public-node-install-20260906/arrow23-wheelhouse \
  pyarrow==23.0.1
```

Selected artifact: `pyarrow-23.0.1-cp313-cp313-macosx_12_0_arm64.whl`.
Downloaded SHA-256 agrees with
[PyPI release metadata](https://pypi.org/pypi/pyarrow/23.0.1/json):
`6b8fda694640b00e8af3c824f99f789e836720aa8c9379fb435d4c4953a756b8`.
PyPI reports upload time `2026-02-16T10:10:45.487047Z`; retrieval and local
verification occurred on 2026-09-06. The macOS 12+ arm64 CPython 3.13 wheel is
compatible with the observed macOS 26.6.2/Python 3.13.13 environment.

`requirements/public-node-macos-arm64-py313.txt` changes only the PyArrow entry
from 21.0.0 to 23.0.1 and its exact wheel hash. New dependency-lock SHA-256:
`50523dc729c4266a7df103cbc2678bab762351f9dc323b610a26b539d0313212`.
The other 13 dependency versions and hashes are unchanged. Their staged wheels
were copied into the new `arrow23-wheelhouse` directory and remain hash-checked
by the existing installation verifier.

## Completed installed proof and policy binding

The refreshed proof passed at `2026-09-06T03:27:23.856799+00:00` with the
main task's explicit ratio-measure policy correction included. A pre-correction
source snapshot and build in `arrow23-build-source` / `arrow23-node-wheel`
remain unused staging, not accepted installation evidence. The accepted local
proof instead uses a fresh source snapshot `arrow23-policy-build-source`,
application wheel `arrow23-policy-node-wheel/rareburden-0.3.0rc2-py3-none-any.whl`
and new output directory `arrow23-policy-proof`.

The existing, unchanged `scripts/verify_public_node_install.py` executed with
the updated dependency lock, `arrow23-wheelhouse`, the application wheel and
exact digest below, the original public-data source root and the new proof
directory. The full installed `--survey` invocation passed under macOS
`sandbox-exec` network denial, with a required `EPERM` network probe. A fresh
venv installed all 15 exact-hash runtime/application wheels using isolated pip,
no cache, no index and no source distributions; `pip check` passed. Installed
imports originated in the clean venv. Three CLI query receipts, embedded
result digests, delivery sidecar and recovery preserving delivered bytes all
verified. The separate descriptive-core probe retained its own two-receipt
store. No prior directory or policy store was reset or reused.

The survey now reserves `survey_weighted_ratio_with_taylor_se` with no
dimensions. The survey CLI explicitly allows that measure alongside count;
legacy/default count-only policies do not grant ratio permission. This is a
deliberate policy/source change, separate from the dependency upgrade, not a
claim that all six application/policy modules are unchanged.

| Artifact | SHA-256 |
| --- | --- |
| Application wheel | `1602fa559f014ae493caeeaccd429f126c8e643e6938362b85d6381bfbea8de3` |
| Combined installation lock | `8311625d1bff1a1d7409af0091e7ac650d9bf4e1e3289f85001fbba236056b84` |
| `arrow23-policy-proof/receipt.json` | `7dee917a24b4ab329a92ecc02bc40fdf9e5f7952c56d420baf2e5604246aadcb` |
| Unchanged installation verifier | `1e4c574445f51d1b640bce5167fef53fa33662ece2ce8ef11764041312c6ef71` |
| Delivered result bundle | `249d11223d2f2906ce3f2c7e63798e2648dcd17043e48a488bae2157e6cf97d5` |
| Installed `public_node.py` | `592acdf2e4ae110d968daee9f2693e2177a527ce701fa5bf74383318dc5ba3d2` |
| Installed `public_node_cli.py` | `4890d3cdeb0c1ed423a815ce8f85af243f05d25ab272e9b20ff55f0f2f7ab2b7` |
| Installed `public_survey.py` | `49166cc2cd91e8c6bbe648c15c079a025fb2aba9c132a2b8b450bce592200e90` |
| Installed `public_delivery.py` | `72d87c1f88a8518f6393107acdcfdd4c61cbcaca3ead8637e8599d35aa7af605` |
| Source and installed `node_policy.py` | `37c5cf3295ae1e61ff681e8e4d96ab1b752a2238a4a1b02ea1219b494f5d47f0` |
| Source and installed `node_policy_store.py` | `eb74c31b2fe279636d107554741e5d687fe1bb611cb1140ca7924dbdd5d947ca` |

The four public-module digests are in the installation receipt. The additional
policy-module source/installed equality checks are retained in the comparison
receipt below. Qualification is for the exact built wheel and source snapshot;
later documentation/resource changes create a distinct wheel artifact.

## Scientific projection agreement

The external `arrow23-compare.py` script first verified both result files
against their retained installation receipts, then compared every result field
except these explicitly operational/query metadata fields:
`output_sha256`, `policy_sha256`, `query_dimensions`, `query_measure`,
`query_sha256`, `receipt_chain_sha256`, `receipt_sequence`, and `recorded_at`.
The added query measure/dimensions are excluded because the repair makes the
policy contract explicit; their difference is intentional, not hidden output
equivalence. Input pins, actual scientific values, methods, scope, suppression
and limitations remain part of the comparison.

All three scientific projections exactly equal the previous `final-proof`.
Canonical JSON uses sorted keys, compact separators and rejects NaN. Both
projection SHA-256 values are
`ae4604f06ce38e3f6e087ccc4c0d0d9bf8b20b6f83a36efb4bafb4def9190fc3`.
The prior receipt still hashes to
`247d1710e54da9586c65533924144011d5088c32c0662aa493467d9e0e49c72e`.

- `arrow23-comparison.json` SHA-256:
  `73f5cf9d8c168545b80ebef568cd8d6bc367bc01d50c8f7227f315ff7b21753a`.
- `arrow23-compare.py` SHA-256:
  `39b6fe6bfe677f3179a99186e389671029c39be091fd2d4fcc205a336bb58b29`.

The existing verifier self-tests also passed. Full repository checks, the
main task's policy regression tests, fresh hosted Actions and merge status
must be reported separately; this local proof does not claim their completion.

All `arrow23-...` external artifacts are beneath
`/Volumes/PortableSSD/rbd-public-data/public-node-install-20260906`.
Earlier immutable candidate manifests, prior proof directories and the
[historical installation evidence](track-004-public-node-installation.md)
remain unchanged. Only hashes and equality results are recorded here; no
row-level or small-cell outputs were copied into Git. As with earlier proofs,
the capsule assumes a preinstalled compatible Python/venv/ensurepip and macOS,
and does not prove bare-machine bootstrapping, other platforms, independent
operation, custodian deployment, clinical validation or release acceptance.
