# Track 002 specification — Public-source acquisition and provenance adapters

## Objective

Implement the reproducible acquisition layer for selected open or routinely accessible public sources without committing third-party bulk data to Git.

## Why this track exists

A source name and URL are not a reproducible data pipeline. Stable burden estimates require immutable retrieval evidence, lawful reuse, source-change detection, normalised units and lineage that survives into released outputs.

## Scope

Initial supported sources:

1. Orphadata Science disease, alignment and epidemiology releases.
2. United Nations World Population Prospects population denominators.
3. One WHO aggregate burden or expenditure release with stable bulk access.
4. World Bank Indicators API as the first query-based covariate adapter.

IHME and OECD acquisition may be registered manually and specified here, but automation proceeds only after current terms and query/export behaviour are tested.

Completion is bounded to the implemented acquisition/provenance substrate,
the exact owner-dispositioned source roles, and fail-closed metadata-only or
exclusion routes. Comprehensive historical, language, country, publisher-
controlled and credentialed acquisition is optional separately versioned work,
not part of this track's acceptance criteria.

## Required outputs

- source-release, acquisition-manifest and normalised-table schemas;
- common adapter and manual-registration interfaces;
- cache, retry, timeout, atomic write and checksum behaviour;
- source-specific configuration, licence notes and operator instructions;
- parsers producing normalised, schema-valid tables;
- lawful small fixtures or synthetic fixtures for offline tests;
- provenance links from normalised rows to acquisition manifests;
- one end-to-end public-data acquisition example;
- extended catalogue fields for geography level, representativeness and verification state.

## Acceptance criteria

1. A clean user can install and run all tests without network access.
2. An authorised user can acquire or register each supported source through one documented command.
3. Re-running a pinned release yields the expected checksum or an explicit source-change failure.
4. Partial or malformed downloads cannot enter analysis.
5. Raw third-party files remain outside Git and retain source-specific terms.
6. Normalised outputs identify source release, geography, age/sex where relevant, unit and transformation version.
7. Licence and access-test states are distinct from metadata review.
8. A clean reference workflow reaches a schema-valid normalised table and manifest.

## Non-goals

- circumventing login, rate limits or click-through terms;
- mirroring data whose terms prohibit redistribution;
- assuming all source updates are backwards compatible;
- using a source in public analysis before terms and provenance are recorded.
- completing every discoverable historical release, language, national edition
  or publisher-controlled source;
- publishing the prepared Orphadata/MONDO candidate or reconciling an existing
  hosted object without a separate exact external authorization.

## v1 contribution

This track supplies the public acquisition and provenance substrate required by V1-DATA-01 to V1-DATA-03 and V1-ENG-05.
