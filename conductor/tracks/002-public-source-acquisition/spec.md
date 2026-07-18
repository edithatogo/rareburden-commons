# Track 002 specification — Public-source acquisition and provenance adapters

## Objective

Implement the first reproducible acquisition layer for selected open or routinely accessible public sources without committing third-party bulk data to Git.

## Initial source set

1. Orphadata Science disease, alignment and epidemiology releases.
2. United Nations World Population Prospects population denominators.
3. One WHO aggregate burden or expenditure release with stable bulk access.
4. World Bank Indicators API as the first query-based covariate adapter.

IHME and OECD adapters may be specified in this track but should only be implemented after their current terms, registration and query-export behaviour are tested manually.

## Required outputs

- a common adapter interface;
- source-specific configuration and acquisition instructions;
- local download cache excluded from Git;
- immutable acquisition manifests containing source, release, URL/query, retrieval time, licence note, file size and checksum;
- parsers that emit normalised, schema-validated tables or metadata;
- small lawful fixtures or synthetic fixtures for offline tests;
- provenance links from transformed tables to acquisition manifests;
- one end-to-end public-data example.

## Acceptance criteria

1. A clean user can install dependencies and run tests without downloading large data.
2. An authorised user can acquire each implemented source through one documented command or manual-download registration step.
3. Re-running against the same source release produces the same checksum or an explicit source-change failure.
4. Raw third-party files remain outside Git and retain source-specific terms.
5. Normalised outputs identify source release, transformation version, geography and unit.
6. Failed, partial or changed downloads cannot silently enter analysis.
7. The end-to-end example contains no controlled or participant-level data.

## Non-goals

- automated circumvention of login, rate limits or click-through terms;
- mirroring sources whose licences prohibit redistribution;
- building the burden model before source provenance is stable;
- treating all source updates as backward compatible.
