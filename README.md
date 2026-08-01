# RareBurden Commons

> Open, reproducible infrastructure for measuring the collective health, social and economic burden of rare diseases.

RareBurden Commons is the working technical repository of the **Global Rare Disease Burden Initiative**. It uses public aggregate data directly and is designed to run controlled analyses behind custodian boundaries rather than centralising patient records.

## Status

**Hardened v0.3.0rc2 handoff candidate; not a final v0.3.0 scientific release.**

The repository preserves the released v0.1.0 and v0.2.0 history and now implements substantially more of the v0.3 foundation:

- fail-closed public-source acquisition and manual release registration;
- source-release, acquisition and normalisation manifests;
- normalisers for Orphadata-style XML, UN-style population CSV, WHO-style aggregate CSV and World Bank indicator responses;
- versioned semantic hierarchy and overlap-safe aggregation primitives;
- evidence, parameter, quality and transportability records;
- deterministic and Monte Carlo expected-population and rare-aetiology count calculations;
- public-data gap mapping;
- prospective protocol and decision transparency;
- activity-level provenance, lineage closure, W3C PROV-O, RO-Crate/Process Run Crate and GATHER evidence;
- conservative R0–R4 reproducibility claims;
- a synthetic, offline, independently verified reference release;
- hardened CI/CD, dependency-lock, package, SBOM and workflow-policy controls.

All executable examples are synthetic assurance fixtures. The repository does **not** publish an empirical rare-disease burden estimate, imply custodian approval, or claim independent reproduction, external replication or constituted programme governance.

## Start here

### Programme and scientific foundation

- [Vision, mission and purpose](docs/vision-mission-purpose.md)
- [Strategy](docs/strategy.md)
- [MoSCoW requirements](docs/requirements.md)
- [System architecture](docs/design/architecture.md)
- [Public-data-first protocol](docs/protocols/public-data-foundation.md)
- [Current handoff status](docs/handoff/implementation-status.md)
- [Role-based guides](docs/guides/README.md)
- [Quickstart](docs/guides/quickstart.md)
- [Synthetic reference workflow tutorial](docs/tutorial-reference-workflow.md)
- [Documentation quality and correction guidance](docs/documentation-guidance-017.md)

### Route to stable v1.0

- [Roadmap](docs/roadmap-v1.md)
- [Conductor track register](conductor/tracks.md)
- [Machine-readable roadmap](conductor/roadmap.yml)
- [Maturity model](docs/maturity-model.md)
- [Stable v1 acceptance criteria](docs/v1-acceptance-criteria.md)
- [Requirements traceability](docs/requirements-traceability.md)
- [Testing strategy](docs/testing-strategy.md)
- [Release policy](docs/release-policy.md)
- [Risk register](docs/risk-register.md)

## Release sequence

| Release | Outcome |
|---|---|
| v0.1.0 | Founding strategy, architecture, protocol and source catalogue |
| v0.2.0 | Programme control plane and stable-v1 contract |
| v0.3.0 | Public acquisition, novelty decision and auditable scholarly provenance |
| v0.4.0 | Governed semantic hierarchy and evidence/parameter core |
| v0.5.0 | Validated burden engine and monogenic-diabetes demonstrator |
| v0.6.0 | Federated node and bronchiectasis demonstrator |
| v0.7.0 | Economic/social burden and paediatric demonstrator |
| v0.8.0 | Quality-assured atlas and API beta |
| v0.9.0 | Constituted governance and operational release candidate |
| v1.0.0 | Stable, independently reproducible and supportable infrastructure |

Progress is gate-based, not date-driven. The exact exit conditions are in `conductor/roadmap.yml`.

## Core design principle

> **Link estimates, not identities.**

Sensitive records remain with their custodians. Approved nodes execute common, versioned analyses and return disclosure-controlled aggregate outputs.

## Repository map

```text
conductor/              Persistent product context, roadmap and tracks
catalog/                Data-source and adjacent-initiative registers
docs/                   Strategy, protocols, design and assurance guidance
schemas/                Normative machine-readable scientific contracts
examples/               Synthetic fixtures and executable reference inputs
src/rareburden/          Acquisition, modelling, provenance and verification code
tests/                   Unit, integration, security and scientific-contract tests
scripts/                 CI, build, reproducibility and release harnesses
outputs/                 Local reproducible non-sensitive outputs
```

## Local verification

With a supported Python and the locked development environment:

```bash
uv sync --frozen --extra dev
uv run make check
uv run make reproducibility
```

A dependency-limited environment can still run the core offline checks:

```bash
PYTHONPATH=src:. python -m rareburden validate-programme
PYTHONPATH=src:. python scripts/check_schemas.py
PYTHONPATH=src:. python -m pytest -o addopts='' --ignore=tests/test_burden.py
```

The property-based burden tests require Hypothesis and the complete release harness requires the locked development dependencies.

## Synthetic reference release

```bash
PYTHONPATH=src:. python -m rareburden demo-public-foundation \
  --root . \
  --output outputs/public-foundation-synthetic \
  --created-at 2026-07-27T00:00:00Z \
  --overwrite
```

The resulting package contains source snapshots, acquisition and transformation records, quality dispositions, analysis outputs, a gap map, workflow provenance, a lineage audit, PROV-O, RO-Crate metadata, GATHER evidence and a conservative reproducibility assessment.

Verify the closed package independently:

```bash
PYTHONPATH=src:. python -m rareburden verify-reference-release \
  --root . \
  --release outputs/public-foundation-synthetic \
  --verified-at 2026-07-27T00:00:00Z
```

A passed report establishes internal structural and deterministic auditability (R2), not empirical validity, independent reproduction, external replication or approval.

## Safety boundary

Never commit participant-level, row-level, small-cell, controlled or otherwise sensitive health data. Public Git is restricted to code, public metadata, synthetic fixtures and explicitly approved disclosure-controlled outputs.

## Working name

“RareBurden Commons” remains provisional and should be tested with patient organisations, country partners and prospective institutional hosts before public launch.

## Licensing

Reference code is Apache-2.0. Original documentation and catalogue metadata are intended as CC BY 4.0. Third-party data retain their own terms; see `LICENSE-DATA.md`.
