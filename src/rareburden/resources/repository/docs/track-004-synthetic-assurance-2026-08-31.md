# Track 004 bounded synthetic assurance — 2026-08-31

Status: local engineering evidence for an exact candidate, not Track 004
completion, production activation, custodian approval or node-alpha release.

## Candidate and retained evidence

- Candidate commit: `9fd347ecbaf821fc0d73fe09c77760bf0484c3d5`.
- Candidate tree: `c6edd93f21a28fd578e38d94762bf749f5efa7e0`.
- Input manifest: `manifests/node/track004-assurance-inputs-20260831.json`.
- Input-manifest SHA-256:
  `8355763db05b3655ede51ee3c7b52d2525dbf91988371559ae5a26018722c9b8`.
- Actual installation stdout: `manifests/node/track004-offline-install-20260831.json`.
- Installation-receipt SHA-256:
  `174bade39a10013b84ffd806c9052be10966eff40d71898f19e4eff514183ade`.

The manifest and receipt are full-checkout resources, not installed documentation
assets. This later evidence commit is not the wheel that was rehearsed. Changes
to packaged documentation change wheel bytes; do not transfer the recorded wheel
digest to later builds. No Track 003 retained analysis was rerun.

## Observed installation and bundle checks

The owner-directed agent executed the fixed one-row synthetic engineering fixture
on macOS arm64 (Darwin 25.6.0), using the preprovisioned Python 3.13.13 environment
and uv 0.11.8. The requested clean-environment selector was `3.13`; the installer
receipt itself does not attest a Python patch version. Runtime selection was
checked with `uv python find 3.13` before interpreting the receipt.

Preparation downloaded seven dependency wheels using pip's `--require-hashes
--only-binary=:all:` against the bound `requirements.txt`. This phase permitted
network access and is not offline evidence. The project wheel was built from the
clean committed candidate with the deterministic repository builder and fixed
source-date epoch `1760000000`.

The measured invocation, with the temporary dependency directory replaced by the
non-sensitive placeholder `<staged-dependencies>`, was:

```sh
.venv/bin/python scripts/check_offline_node_install.py \
  --node-wheel dist/rareburden-0.3.0rc2-py3-none-any.whl \
  --wheelhouse <staged-dependencies> --python-version 3.13
```

The command started around `2026-08-31T10:05:52Z` and exited zero. It created a
fresh temporary environment, installed only from the staged wheelhouse, checked
dependency compatibility, and executed the installed module with isolated Python
imports from an unrelated directory. Stdout records one row and the exact expected
synthetic fingerprint, plus pre/post-verified hashes for all eight wheels.
`network_disabled` means package-command settings, not an OS firewall measurement.

Those same eight artifacts were assembled using `build_node_bundle.py build`,
then checked using `build_node_bundle.py check`; both exited zero and returned
identical manifests. The local transport ZIP SHA-256 was
`a8c7dbbdd7842c201af2e8675118f13440b26b82db43d21b438ec35cb64d80e1`.
Generated wheels and the ZIP remain local build artifacts, not published or signed
release artifacts. This records the installation and transport checks, not every
API or operational procedure described in the operator guide.

## Advisory review and remaining gates

Panel assurance: simulated role-separated advisory panel. Engineering,
privacy/security, and operator/community-harm agents challenged the bounded diff.
Implementation ownership and cross-review were separated: the installer engineer
reviewed the store, the store/security agent reviewed the installer, and a third
agent challenged operator claims. The initial installer finding (a wrong but
self-consistent output digest could pass) was fixed and re-reviewed before the
candidate commit. No blocking finding remained in the reviewed bounded scope.

Owner-executed simulated-community challenge; no actual community participation,
representation, consultation, endorsement, consent or independent review.

Remaining uncertainty includes privileged history replacement, filesystem races,
artifact authenticity, platform portability, production history-replay costs,
custodian controls and actual stakeholder needs. Stop on input hash drift,
unexpected fixture output, failed checks, tampered history, sensitive data or
claims exceeding this synthetic scope. No dissent was retained against the
bounded engineering tranche; that is not agreement to production activation.

The recommendation is to accept the bounded engineering fixes under the existing
continuation instruction, retaining the original six pending Track 004 plan gates.
Alternatively, defer further production work until a genuine custodian route
exists. A synthetic-only scope amendment is a separate decision requiring revised
acceptance mapping; tests must not silently make that amendment. See the
[review packet](track-004-node-review-packet.md) for options, trade-offs and the
production contract/store/review/release decisions still required.
