# Testing and assurance strategy

## Objective

Testing must establish not only that code executes, but that scientific meaning, provenance, privacy and release behaviour remain correct as sources and methods evolve.

## Test layers

| Layer | Purpose | Representative checks |
|---|---|---|
| Schema | Reject malformed metadata and outputs | Required fields, enums, formats, compatibility fixtures |
| Unit | Verify isolated functions | Parsing, mappings, distributions, calculations, disclosure rules |
| Property-based | Verify invariants over broad inputs | Non-negative populations, bounded fractions, monotonicity, hierarchy conservation |
| Contract | Keep adapters and nodes compatible | Input/output schemas, manifest fields, API responses, version negotiation |
| Integration | Exercise multiple components | Acquire/register → normalise → ledger → model → release |
| Statistical | Verify numerical and inferential behaviour | Coverage, convergence, seed reproducibility, sensitivity and boundary conditions |
| Scientific golden tests | Detect unintended interpretation changes | Approved reference estimates, mappings and overlap cases |
| Privacy/disclosure | Prevent unsafe output | Small cells, differencing, rare combinations, log redaction and export rules |
| Security | Reduce supply-chain and code risk | Secrets, dependencies, static analysis, SBOM and signature verification |
| Performance | Protect practical usability | Time, memory and file-size budgets on reference workloads |
| Reproducibility | Confirm clean rebuilds | Source archive, Git clone, locked environment and independent run |
| Documentation | Keep instructions executable | Code examples, links, CLI help and tutorials |
| Accessibility | Keep products usable | Text alternatives, keyboard navigation and colour-independent meaning |

## Scientific invariants

The test suite must include cases demonstrating that:

- expected affected population cannot be negative;
- a rare-aetiology fraction remains within zero and one unless explicitly represented as an invalid input;
- parent and child disease entities are not summed into the same mutually exclusive total;
- a person with multiple diagnoses is not automatically counted as multiple people;
- changing an ontology mapping changes the release manifest and invalidates stale outputs;
- uncertainty increases or remains unchanged when an additional independent uncertainty source is introduced;
- incompatible units, periods, populations or metrics do not combine silently;
- case fractions are not automatically applied to mortality, DALY or cost envelopes without an explicit outcome model;
- simulation results reproduce from recorded seeds and package versions;
- disclosure settings cannot be weakened below the active custodian policy by an analysis author.

## Coverage targets for v1.0

- at least **85%** overall line coverage;
- at least **95%** line and branch coverage for provenance, hierarchy, burden-calculation and disclosure-control modules;
- every resolved production defect receives a regression test where technically possible;
- excluded lines are documented and reviewed rather than blanket-ignored.

Coverage is a floor, not evidence of scientific validity.

## Compatibility matrix

The v1 release candidate must test:

- all supported Python versions;
- supported operating systems or container runtime;
- current and previous compatible schema fixtures;
- clean Git clone and source archive;
- offline node execution;
- representative small and large public workloads;
- migration from the most recent beta release.

## Test data policy

Public tests use:

- synthetic records;
- small redistributable fixtures;
- deliberately malformed fixtures;
- approved aggregate examples;
- generated edge cases.

No participant-level, controlled, small-cell or licence-restricted data are committed. Controlled environments may run an additional local test suite whose inputs and outputs remain under custodian governance.

## Release evidence

Each release candidate stores:

- exact commit and environment;
- test inventory and results;
- coverage and benchmark reports;
- scientific golden-test version;
- security and dependency findings;
- documentation and accessibility results;
- reproduction report;
- accepted exceptions with owner and expiry condition.
