# RareBurden Commons

> Open, reproducible infrastructure for measuring the collective health, social and economic burden of rare diseases.

RareBurden Commons is the working repository of the **Global Rare Disease Burden Initiative**. It is being designed as a public-data-first, federated evidence platform rather than a central repository of patient records.

## Status

**Foundation / pre-protocol v0.1.** The repository currently defines project context, requirements, architecture, governance principles and the first analytic protocol. It does not yet publish burden estimates.

## Start here

- [Vision, mission and purpose](docs/vision-mission-purpose.md)
- [Strategy](docs/strategy.md)
- [MoSCoW requirements](docs/requirements.md)
- [System architecture](docs/design/architecture.md)
- [Public-data-first protocol](docs/protocols/public-data-foundation.md)
- [Conductor context](conductor/index.md)

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

## Safety boundary

No patient-level, row-level or otherwise sensitive health data may be committed to this repository. Synthetic, public aggregate and disclosure-controlled data only.

## Working name

“RareBurden Commons” is provisional and should be tested with patient organisations, country partners and prospective institutional hosts before public launch.
