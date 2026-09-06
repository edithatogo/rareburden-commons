# Track 004 — Public-node installed-runtime evidence

## Scope and current disposition

The public-node dependencies have a separate exact-wheel lock for CPython 3.13
on macOS arm64. Both the preliminary **descriptive-only** run and the corrected
**survey-inclusive installed CLI** run passed with network access denied on
2026-09-06. The corrected run follows source-aware handling of finite fractional
ages below one, retained outside the adult analysis domain without rounding.
No missing ages were found; raw XPT and Parquet decoded equally through pandas,
which does not independently validate the SAS decoder. See the
[survey method](track-004-public-survey-method.md) for the bounded decision.
Packaged resources were synchronised before the corrected snapshot. Later
documentation updates do not change the source-module hashes below, but they
do require a new wheel receipt before claiming exact final-package qualification.

This is agent-executed, owner-authorised, same-host evidence, not independent
operation, custodian acceptance, clinical validation or release authorisation.
No participant rows, category counts or small-cell results are recorded here.

## Locked dependency capsule

The platform-specific lock `requirements/public-node-macos-arm64-py313.txt`
contains every third-party runtime dependency, including pandas and PyArrow.
Every entry is an exact version and SHA-256 of the selected wheel; no source
distribution or dependency resolution from an index is allowed during proof.
Its SHA-256 is
`d533fd8a4c08f972152bcbfd051713bf38fc570f9a4cbc84a8433431e310c22f`.

Selected versions: attrs 26.1.0, defusedxml 0.7.1, jsonschema 4.26.0,
jsonschema-specifications 2025.9.1, NumPy 2.5.2, pandas 2.3.3, PyArrow 21.0.0,
python-dateutil 2.9.0.post0, pytz 2026.3.post1, PyYAML 6.0.3, referencing 0.37.0,
rpds-py 2026.6.3, six 1.17.0 and tzdata 2026.3. The selected NumPy wheel requires
macOS 14 or newer; the actual observed host is macOS 26.6.2 arm64, Python 3.13.13.

The dependency wheelhouse is retained outside Git at
`/Volumes/PortableSSD/rbd-public-data/public-node-install-20260906/wheelhouse`.
Core dependency downloads used the existing repository `requirements.txt` with
hash enforcement. The seven additional dependencies were freshly downloaded
from pip's default index with `--isolated --no-cache-dir --only-binary=:all:
--no-deps`, then the exact downloaded hashes were recorded in the separate lock.
This is acquisition plus local hash binding, not an independent provenance
attestation or vulnerability audit. No dependency wheel was published.

The application wheel is **separately exact-bound** through the verifier's
mandatory `--expected-node-sha256`; its hash is added to an external combined
installation lock, along with all 14 dependencies. The source package version
alone cannot identify the candidate because it remains `0.3.0rc2` during work.

## Verifier contract and reproducible invocation

Verifier: `scripts/verify_public_node_install.py`:

1. Rejects missing, ambiguous or changed wheels and malformed/duplicate lock
   entries before creating the proof directory.
2. Creates a new external proof directory exclusively; copies and rehashes all
   locked wheels and retains the exact verifier and installation lock.
3. Starts `sandbox-exec -p '(version 1) (allow default) (deny network*)'`.
   A loopback socket probe must fail specifically with `EPERM`; an unreachable
   endpoint, missing tool or ordinary connection refusal is not accepted.
4. Creates a fresh virtual environment and installs with isolated pip,
   `--no-cache-dir --no-index --only-binary=:all: --require-hashes --find-links`.
   `pip check` must pass. The subprocess environment supplies only a system
   `PATH`; Python runs with `-I`, without source `PYTHONPATH` or user-site imports.
5. Runs the **installed** `python -I -m rareburden.public_node_cli --survey`
   against pinned UCI, DIQ and DEMO files, then runs `--recover` and requires
   unchanged delivered bytes. Every result's embedded digest, including the
   survey result, must match its canonical content, and the delivery sidecar
   must match the complete result file. The CLI policy store must contain three receipts.
6. Separately imports pandas, PyArrow and the public-node modules from that new
   environment, verifies their import locations, runs the pinned descriptive
   core with its own two-receipt store, verifies result digests and records only
   hashes and environment metadata. Installed versions and retained wheel
   hashes must still match the lock before a success receipt is emitted.

Example invocation after explicitly building and hashing the intended wheel
(replace `CANDIDATE_SHA256` and the new proof-directory name):

```sh
.venv/bin/python -I scripts/verify_public_node_install.py \
  --lock requirements/public-node-macos-arm64-py313.txt \
  --wheelhouse /Volumes/PortableSSD/rbd-public-data/public-node-install-20260906/wheelhouse \
  --node-wheel /absolute/path/to/rareburden-0.3.0rc2-py3-none-any.whl \
  --expected-node-sha256 CANDIDATE_SHA256 \
  --source-root /Volumes/PortableSSD/rbd-public-data \
  --output /Volumes/PortableSSD/rbd-public-data/public-node-install-20260906/NEW-PROOF
```

Never retry a failed analysis by resetting its policy database. Failed proof
directories remain evidence; a separately authorised rehearsal needs a new
directory. The verifier's success record is `receipt.json`, not the existence
of a virtual environment, install log or partial computation file.

## Preliminary descriptive-only observation

Observed at `2026-09-06T02:28:22.785099+00:00`, using the pre-survey wheel:

- Wheel: `3e6a2dab0d6b6e2e0f07aa5ca2c6ea73793e832dbfe8dcf7f4b4af17970d081f`.
- Combined lock: `1d424c640ed590ea83ced69b90ce1475ff7c0b5e55a63255b86241a44a9491a1`.
- Earlier verifier: `6928e26dd7c5ec0227f3071ece5138289bd1a3861f8cea54a2c72f5302baa933`.
- Receipt: `29a36cf5d9f70653d618dd3bf6e95185a1c96ae670ae519d97c788329e204ccf`.
- External evidence directory: `public-node-install-20260906/preliminary-proof`
  beneath the external data root above; network probe `EPERM`, `pip check`
  passed, installed imports passed, and two descriptive query receipts verified.

This earlier verifier did not execute the installed survey CLI or its recovery
path. Its retained source is `preliminary-proof/verify.py`; the current verifier
has additional checks, exercised against the corrected candidate below.

## Corrected survey-inclusive installed proof

Observed at `2026-09-06T02:35:16.285061+00:00`. A new source copy in
`public-node-install-20260906/corrected-build-source` was built using
`python -m build --wheel --no-isolation --outdir .../corrected-wheel`.
The invocation above used `corrected-wheel/rareburden-0.3.0rc2-py3-none-any.whl`,
the exact hash below, and the new directory `public-node-install-20260906/corrected-proof`.
All paths here are beneath `/Volumes/PortableSSD/rbd-public-data`.

- Application wheel SHA-256:
  `b057cf092934b2c79d39f89035300104c3098cfb930a1e977c359aad48921756`.
- Combined installation lock SHA-256:
  `5f8c29d8639152ff65b3c0b409d4315fdb7547bd9eb7a7aabcde5a329e85ebe2`.
- Verifier SHA-256:
  `1e4c574445f51d1b640bce5167fef53fa33662ece2ce8ef11764041312c6ef71`.
- `corrected-proof/receipt.json` SHA-256:
  `aeb45390b06b141c7fb334c7b56a1398114356f041478eb98b5bc71e925d8c6d`.
- Delivered CLI bundle SHA-256:
  `03704a9246d35db40fda2482b5b8c57400083d87a5e6df9fbda6e4246cabf70a`.

The fresh venv installed all 15 locked application/runtime wheels without index
or cache use, under enforced network denial (`EPERM`). `pip check` passed.
Installed `--survey` execution returned the required three-result bundle and
three durable query receipts; the separate descriptive-core import probe
verified two receipts in its own store. Every embedded result digest and the
delivery sidecar matched. Installed `--recover` preserved the delivered bytes
and the three-receipt store. This is successful delivery/recovery invocation
evidence, not an injected power-loss experiment.

Exact installed source-module SHA-256 values, also verified to match the source
snapshot at build time:

| Module | SHA-256 |
| --- | --- |
| `public_node.py` | `592acdf2e4ae110d968daee9f2693e2177a527ce701fa5bf74383318dc5ba3d2` |
| `public_node_cli.py` | `173526c825313ff96eb915673b270dc3d3899497133542af3285e55a084da506` |
| `public_survey.py` | `9171df12381cffde21bb9baf8c4572cfc47b037e06237b74f95845554871683a` |
| `public_delivery.py` | `5eedb0e85067137077582ef545f935ceb156957208079161c9df2ec3f6d6df59` |

The receipt also records all dependency wheel hashes, installed versions,
interpreter executable hash, input pins and output hashes, but no row-level or
small-cell values. The top-level `population_estimate: false` describes the
separate descriptive probe; `installed_cli_survey` explicitly identifies the
additional experimental survey candidate. Neither is clinical validation.

## Final installed proof including parent-directory durability fix

The final code candidate was rebuilt after resource synchronisation and the
parent-directory fsync fix. The earlier corrected proof above remains historical
evidence and does **not** qualify that later fix. The new proof passed at
`2026-09-06T02:38:05.701533+00:00`, retaining evidence beneath
`/Volumes/PortableSSD/rbd-public-data/public-node-install-20260906/final-proof`.
Its source snapshot and wheel are retained in sibling `final-build-source` and
`final-wheel` directories. The documented verifier invocation used that wheel,
its exact digest below, and the new `final-proof` output directory.

- Application wheel SHA-256:
  `55e01851dea9318b701e6ae8abf736381164761afc60b1e52480c91f86019703`.
- Combined installation lock SHA-256:
  `5eb4dcff2f764f3c1a27c8950532980e5fa81d632d242a8056b4939c48a638bf`.
- `final-proof/receipt.json` SHA-256:
  `247d1710e54da9586c65533924144011d5088c32c0662aa493467d9e0e49c72e`.
- Delivered CLI bundle SHA-256:
  `a7f4454f7f4dc4cfbf97bfab41ca22186bf3215e0999d7155165a59f2485b5f7`.
- Installed `public_delivery.py` SHA-256:
  `72d87c1f88a8518f6393107acdcfdd4c61cbcaca3ead8637e8599d35aa7af605`.
- Installed `public_node_cli.py` SHA-256:
  `77b33d09a6063ce33d8da2b939777737f7293d4499e7b7fd126e7c5de6ecd9e6`.

The counting and survey module hashes, dependency lock and verifier are
unchanged from the corrected proof. All four installed application module
hashes match the final build-source snapshot. Network `EPERM`, isolated
no-cache/no-index hash-required installation, `pip check`, installed imports,
the three-receipt survey CLI, embedded result/sidecar digests and recovery
preserving delivered bytes all passed again. No previous proof directory or
policy store was reset or reused. This qualifies the exact wheel and source
modules above; recording these results subsequently changes documentation, not
the qualified code. Any later rebuilt wheel remains a distinct package artifact.

## Verification and limitations

`python -I scripts/verify_public_node_install.py --self-test` passes lock parser
positive/rejection checks, changed-byte detection, wrong application hash and
missing dependency rejection without creating an installation directory.
Ruff check and formatting pass for the verifier. Both full installed executions
above are additional end-to-end tests, not unit-test substitutes. Final shared
repository checks remain the main task's responsibility after all changes.

The capsule assumes a preinstalled compatible Python interpreter with `venv`
and bundled `ensurepip`, plus macOS and its system libraries. Preliminary pip
was 26.0.1 from `ensurepip`; these prerequisites are not shipped by the runtime
lock. This proves no cached **application dependencies** are needed; it does
not prove bare-machine OS/Python bootstrapping, another host, Linux or Windows.

Build staging was online-capable; installation and real-data computation were
network-denied. Builds used a copied source snapshot outside Git and
`python -m build --wheel --no-isolation`; the build-tool environment is not
covered by the application-runtime lock, and reproducible wheel builds are not
claimed by this evidence. Later source/resource changes require a new exact
candidate wheel and receipt. Package installation is not clinical validation,
survey-method validation, production hardening, custodian deployment or a
release decision. External paths are local evidence locations, not durable
public archives or attributable third-party acceptance receipts.
