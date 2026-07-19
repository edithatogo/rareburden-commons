# RareBurden Commons

> Open, reproducible infrastructure for measuring the collective health, social and economic burden of rare diseases.

RareBurden Commons is the working repository of the **Global Rare Disease Burden Initiative**. It is designed as a public-data-first, federated evidence platform rather than a central repository of patient records.

## Status

**Programme-control release v0.2.0 complete; v0.3.0 evidence-acquisition work active.**

The repository now contains a complete, machine-validated Conductor delivery system from the foundation to a stable v1.0. It defines 17 tracks across 10 gated releases, a maturity model, blocking v1 acceptance criteria, requirements traceability and a programme risk register.

Implemented code currently validates the source catalogue and programme roadmap. It does **not** yet acquire external data, run burden models or publish burden estimates. Those capabilities are assigned to explicit downstream tracks and must not be represented as complete.

## Start here

### Programme and scientific foundation

- [Vision, mission and purpose](docs/vision-mission-purpose.md)
- [Strategy](docs/strategy.md)
- [MoSCoW requirements](docs/requirements.md)
- [System architecture](docs/design/architecture.md)
- [Public-data-first protocol](docs/protocols/public-data-foundation.md)

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
| v0.2.0 | Complete programme control plane and stable-v1 contract |
| v0.3.0 | Public-source acquisition and novelty validation |
| v0.4.0 | Semantic hierarchy and evidence/parameter ledger |
| v0.5.0 | Public burden engine and monogenic-diabetes alpha |
| v0.6.0 | Federated node and bronchiectasis alpha |
| v0.7.0 | Economic/social and paediatric beta |
| v0.8.0 | Quality-assured atlas and API beta |
| v0.9.0 | Governance and operational release candidate |
| v1.0.0 | Stable, independently reproducible and supportable release |

Progress is gate-based rather than date-driven. The detailed exit conditions are in `conductor/roadmap.yml`.

## Core design principle

> **Link estimates, not identities.**

Open aggregate data are used directly. Controlled or sensitive data remain with their custodians and contribute through approved secure analyses or disclosure-controlled summary outputs.

## Repository map

```text
conductor/             Persistent product, roadmap, workflow and track context
catalog/               Machine-readable register of candidate data sources
docs/                  Vision, strategy, requirements, design, protocols and assurance
schemas/               Validation schemas for metadata and programme controls
src/rareburden/         Reference implementation and validation utilities
tests/                  Automated checks
data/                   Local-only working data; raw records are not committed
outputs/                Reproducible non-sensitive outputs
```

## Validate the programme-control release

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
make check
```

The complete check validates:

- the public-source catalogue;
- the release roadmap and every Conductor track;
- dependency acyclicity and release assignment;
- automated tests;
- linting and Python compilation;
- obvious secrets and prohibited data files.

Individual commands are also available:

```bash
rareburden validate-catalog
rareburden validate-roadmap
rareburden validate-programme --json
```

Tests and programme validation run without network access.

## Safety boundary

No patient-level, row-level, small-cell or otherwise sensitive health data may be committed to this repository. Synthetic, public aggregate and disclosure-controlled data only.

## Working name

“RareBurden Commons” is provisional and should be tested with patient organisations, country partners and prospective institutional hosts before public launch.

## Licensing

Reference code is Apache-2.0. Original documentation and catalogue metadata are intended as CC BY 4.0. Third-party data retain their own terms; see `LICENSE-DATA.md`.
