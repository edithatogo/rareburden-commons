# RareBurden Commons

> Open, reproducible infrastructure for measuring the collective health, social and economic burden of rare diseases.

RareBurden Commons is the working repository of the **Global Rare Disease Burden Initiative**. It is being designed as a public-data-first, federated evidence platform rather than a central repository of patient records.

## Status

**Foundation v0.1 complete; public-source acquisition track active.** The repository defines project context, requirements, architecture, governance principles, the first analytic protocol and a validated 14-source access catalogue. It does not yet publish burden estimates.

## Start here

- [Vision, mission and purpose](docs/vision-mission-purpose.md)
- [Strategy](docs/strategy.md)
- [MoSCoW requirements](docs/requirements.md)
- [System architecture](docs/design/architecture.md)
- [Public-data-first protocol](docs/protocols/public-data-foundation.md)
- [Conductor context and active track](conductor/index.md)

## Core design principle

> **Link estimates, not identities.**

Open aggregate data are used directly. Controlled or sensitive data remain with their custodians and contribute through approved secure analyses or disclosure-controlled summary outputs.

## Repository map

```text
conductor/             Persistent product, workflow and track context
catalog/               Machine-readable register of candidate data sources
docs/                  Vision, strategy, requirements, design and protocols
schemas/               Validation schemas for metadata and analytic inputs
src/rareburden/         Reference implementation and validation utilities
tests/                  Automated checks
data/                   Local-only working data; raw records are not committed
outputs/                Reproducible non-sensitive outputs
```

## Validate the foundation

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
make check
```

The catalogue validator runs offline. Source downloads are deliberately not part of the foundation track.

## Safety boundary

No patient-level, row-level or otherwise sensitive health data may be committed to this repository. Synthetic, public aggregate and disclosure-controlled data only.

## Working name

“RareBurden Commons” is provisional and should be tested with patient organisations, country partners and prospective institutional hosts before public launch.

## Licensing

Reference code is Apache-2.0. Original documentation and catalogue metadata are intended as CC BY 4.0. Third-party data retain their own terms; see `LICENSE-DATA.md`.
