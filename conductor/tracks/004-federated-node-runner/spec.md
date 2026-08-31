# Track 004 specification — Federated country-node execution package

## Objective

Create a portable, inspectable package that allows an approved custodian to run a versioned RareBurden analysis locally and return only disclosure-controlled, schema-valid aggregate outputs.

## Required outputs

- node input, output, execution-manifest and disclosure-policy schemas;
- synthetic cohort generator covering edge cases and multi-diagnosis overlap;
- locked portable runtime with offline installation pathway;
- preflight validation, version negotiation and environment capture;
- common analysis runner and locally configurable disclosure controls;
- small-cell, differencing and rare-combination tests;
- export-review checklist and signed/hashed output package;
- correction, withdrawal and incompatible-version procedures;
- operator, data-steward and reviewer guides;
- one synthetic end-to-end run and a pilot-ready controlled-environment package.

## Acceptance criteria

1. Participant-level rows cannot enter the export package.
2. The node runs without network access after approved installation.
3. Input incompatibility, missing fields and version mismatch fail before analysis.
4. Custodian disclosure policy cannot be weakened by an analysis specification.
5. Synthetic outputs reproduce across supported environments.
6. Logs contain no participant values, credentials or unsafe small cells.
7. A separately recorded owner-operated clean-environment run installs and runs
   the package from documentation alone, with agent-panel challenge and owner
   disposition under ADR-0009; no second operator or independence is claimed.
8. A controlled-environment pilot is either completed before v1 or explicitly excluded from the supported v1 claim.

## Non-goals

- centralising participant records;
- bypassing custodian ethics, security or export review;
- guaranteeing compatibility with every secure research environment;
- replacing local statistical disclosure expertise.

## v1 contribution

This track implements V1-FED-01 to V1-FED-05 and provides the execution substrate for controlled demonstrators.
