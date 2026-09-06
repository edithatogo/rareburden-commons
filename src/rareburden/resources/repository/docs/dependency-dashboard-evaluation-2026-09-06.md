# Dependency dashboard evaluation — 2026-09-06

The Renovate dashboard listed major updates for mypy, setuptools and twine.
They were evaluated together against the current exact-candidate evidence
contracts.

The candidate constraints were temporarily tested as `mypy>=2.3,<3`,
`setuptools>=84,<85` and `twine>=7,<8`. The resolver selected mypy 2.3.1,
setuptools 84.0.0 and twine 7.0.0, adding `ast-serialize`. The existing
2,208-test suite then failed five provenance tests because the changed lockfile
invalidated hash-bound Track 009/010 candidate receipts and deterministic
regeneration artifacts.

The constraints and lockfile were restored. The authoritative suite then
passed all 2,208 tests and the runtime asset projection passed. The upgrades
remain deferred until a separately versioned candidate can deliberately
rebind those historical receipts and complete the required compatibility
review. No historical hashes were rewritten and no dependency update is
claimed as merged.

This disposition addresses the dashboard item transparently: it records the
tested versions, observed failures, restoration evidence and the exact reason
for deferral. A future dependency PR must preserve historical reproducibility
or explicitly introduce a new candidate boundary with its own evidence.
