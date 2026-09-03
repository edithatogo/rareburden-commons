# Consolidated agent-panel audit — 2026-09-03

## Disposition

Repository-only advisory audit passed. Accessibility, security, methods,
usability, harm, reproduction and release-boundary controls are present and
fail closed. The panel is advisory under ADR-0009; it is not independent review,
community authority, custodian approval or empirical validation.

## Findings

- Accessibility contracts and text alternatives pass; rendered assistive-tech
  and real-user assessment remain unperformed.
- Security controls cover threat modelling, redaction, dependency/secret/
  workflow scanning, SBOM/checksum provenance and recovery exercises.
- Owner-operated clean-environment reproduction passes for the synthetic
  installed-wheel workflows; it is not independent reproduction.
- Methods and harm controls preserve missingness, overlap, uncertainty and
  non-extrapolation across Tracks 005, 011, 012, 013, 014 and 017.
- Archive/DOI, production qualification, controlled-data, community-authority
  and stable-release gates remain false.

## Reproducible bundle evidence

The deterministic build command
`uv run python scripts/build_distributions.py --root . --output <dir> --source-date-epoch 1760000000`
produced the current prerelease artifacts (`rareburden-0.3.0rc2`):

- wheel SHA-256: `f1a4e8007286ce11bcaf99ec6ce7678a8cbe0b8571d6898f66ef64983dcd0149`
- sdist SHA-256: `19e2c88015f82c243e09a94bdc95761bcb94cf7cfb8fdb96c112bc296fb628ca`

These hashes are preparation evidence only. No DOI deposit, public archive,
stable tag, publication or release authority is implied.
