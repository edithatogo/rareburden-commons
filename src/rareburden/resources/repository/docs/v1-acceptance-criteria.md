# Stable v1.0 acceptance criteria

**Status:** Blocking release contract  
**Applies to:** RareBurden Commons v1.0.0

## Rule

The stable tag may be created only when every criterion marked **Blocking** has objective evidence. “Planned”, “documented in principle” and “works on a maintainer’s machine” are not completion evidence.

## 1. Product and scope

| ID | Criterion | Class | Required evidence |
|---|---|---|---|
| V1-PROD-01 | Supported users, use cases, outputs and non-goals are frozen for v1 | Blocking | Approved product definition and release notes |
| V1-PROD-02 | All v1-critical tracks are complete and formally reviewed | Blocking | Track metadata, completed plans and review files |
| V1-PROD-03 | Every Must requirement maps to a test, artefact or approved governance record | Blocking | Current traceability matrix with no unexplained gaps |
| V1-PROD-04 | CLI, public Python interfaces, schemas and output contracts have a compatibility policy | Blocking | Versioning and deprecation documentation plus compatibility tests |
| V1-PROD-05 | Known limitations and unsupported interpretations are prominent in user-facing outputs | Blocking | Release review and output inspection |

## 2. Scientific validity

| ID | Criterion | Class | Required evidence |
|---|---|---|---|
| V1-SCI-01 | The protocol family defines disease inclusion, estimands, evidence status, overlap, uncertainty, validation, economics and federated analyses | Blocking | Versioned protocols and approved amendments |
| V1-SCI-02 | Disease and aggregation definitions are versioned and no released analysis silently mixes parent and child entities | Blocking | Hierarchy tests, mapping report and release manifest |
| V1-SCI-03 | Every published estimate identifies whether it is observed, transformed, synthesised, transferred, modelled or assumed | Blocking | Schema validation and sampled output audit |
| V1-SCI-04 | Sampling, mapping, transfer, overlap and structural uncertainty are propagated or explicitly bounded | Blocking | Statistical tests, sensitivity outputs and methods report |
| V1-SCI-05 | Three demonstrators exercise materially different methods: monogenic diabetes, bronchiectasis and collective paediatric burden | Blocking | Reproducible analysis packages and review records |
| V1-SCI-06 | At least one released analysis has been reproduced in a clean owner-operated environment from the public release package | Blocking | Hash-bound reproduction report and checksum comparison |
| V1-SCI-07 | At least one methods output has role-separated agent-panel scientific challenge and an owner disposition | Blocking | Panel response, dissent and owner disposition log |
| V1-SCI-08 | Applicable health-estimate reporting items are completed before release | Blocking | GATHER-aligned checklist or justified not-applicable record |
| V1-SCI-09 | Causal language is used only where the estimand and design support it | Blocking | Scientific language review |

## 3. Data, provenance and interoperability

| ID | Criterion | Class | Required evidence |
|---|---|---|---|
| V1-DATA-01 | At least four supported public-source adapters or manual registrars run through the common acquisition contract | Blocking | Integration tests and acquisition manifests |
| V1-DATA-02 | Source changes, partial downloads, licence uncertainty and checksum mismatch fail safely | Blocking | Negative tests and operator guide |
| V1-DATA-03 | Every released table resolves to source release, retrieval event, transformation, code commit and licence state | Blocking | Automated lineage audit |
| V1-DATA-04 | Geography explicitly records country, subnational level and representativeness where known | Blocking | Schema and catalogue audit |
| V1-DATA-05 | Disease definitions and mappings use stable identifiers and record ontology versions | Blocking | Semantic release and mapping tests |
| V1-DATA-06 | Parameter records include population, period, measure, unit, estimate, uncertainty, quality, transportability and provenance | Blocking | Parameter-ledger schema validation |
| V1-DATA-07 | Schemas have semantic versions, migration paths and backwards-compatibility tests | Blocking | Migration fixtures and compatibility report |
| V1-DATA-08 | Third-party redistribution conditions are enforced in packaging | Blocking | Licence review and release-content audit |

## 4. Modelling and computational reproducibility

| ID | Criterion | Class | Required evidence |
|---|---|---|---|
| V1-MOD-01 | Expected affected-population and rare-aetiology calculations have deterministic reference implementations | Blocking | Unit and golden-reference tests |
| V1-MOD-02 | Simulation outputs are reproducible from recorded seeds and environments | Blocking | Reproduction test from clean environment |
| V1-MOD-03 | Distribution selection, parameter correlation and structural scenarios are explicit | Blocking | Analysis specification and sensitivity report |
| V1-MOD-04 | Invalid operations, including naive application of case fractions to incompatible DALY or cost envelopes, are rejected or require explicit override | Blocking | Negative tests and warning/error policy |
| V1-MOD-05 | Numerical stability, convergence and boundary conditions are tested | Blocking | Property/statistical test report |
| V1-MOD-06 | Reference workloads meet documented performance and memory budgets on a supported research workstation | Blocking | Benchmark record |

## 5. Federated analysis, privacy and disclosure

| ID | Criterion | Class | Required evidence |
|---|---|---|---|
| V1-FED-01 | Node inputs, outputs, environment and disclosure rules are machine-readable and versioned | Blocking | Node contracts and schema tests |
| V1-FED-02 | The node runner operates without exporting participant-level data and can run without internet access where required | Blocking | Synthetic end-to-end test and threat-model review |
| V1-FED-03 | Small-cell, differencing and inferential disclosure controls are configurable by custodian policy | Blocking | Disclosure test suite |
| V1-FED-04 | At least one approved controlled environment has completed a pilot execution, or the release scope explicitly excludes claims requiring controlled data | Blocking | Custodian-approved pilot report or bounded-scope decision record |
| V1-FED-05 | Export review, withdrawal, correction and node-version incompatibility procedures are tested | Blocking | Exercise record and operator runbook |

## 6. Software quality and maintainability

| ID | Criterion | Class | Required evidence |
|---|---|---|---|
| V1-ENG-01 | Supported Python versions and operating environments are declared and continuously tested | Blocking | CI matrix and support policy |
| V1-ENG-02 | Linting, formatting, static typing, unit, integration, contract and end-to-end tests pass | Blocking | Green release-candidate CI |
| V1-ENG-03 | Overall line coverage is at least 85% and critical scientific/provenance modules at least 95%, with justified exclusions | Blocking | Coverage report |
| V1-ENG-04 | Public interfaces and schemas have changelog, deprecation and migration coverage | Blocking | Compatibility test suite |
| V1-ENG-05 | A clean source archive and Git clone both pass the documented verification command | Blocking | Archive and clone verification logs |
| V1-ENG-06 | Generated outputs are deterministic where expected and explicitly non-deterministic components are bounded and recorded | Blocking | Reproducibility tests |
| V1-ENG-07 | No unresolved critical or high-severity defects remain within the supported v1 scope | Blocking | Triage register and release decision |

## 7. Security, supply chain and operations

| ID | Criterion | Class | Required evidence |
|---|---|---|---|
| V1-SEC-01 | A threat model covers public repository, acquisition, build, node execution, API and release boundaries | Blocking | Approved threat model |
| V1-SEC-02 | Secret, dependency, licence and static security scans run in CI | Blocking | Green security workflow |
| V1-SEC-03 | Dependencies are locked for reproducible releases and an SBOM is published | Blocking | Lockfile and SBOM |
| V1-SEC-04 | Release artefacts have checksums, build provenance and a verifiable signature or attestation | Blocking | Release bundle and verification instructions |
| V1-SEC-05 | Incident response, vulnerability disclosure, backup, recovery and rollback procedures are tested | Blocking | Exercise records and runbooks |
| V1-SEC-06 | Supported-version and security-fix policies have named owners | Blocking | Support policy and maintainer roster |
| V1-OPS-01 | Operational metrics, logs and failure alerts avoid sensitive content and have documented retention | Blocking | Operations design and test evidence |
| V1-OPS-02 | Metadata and release registries can be restored from documented backups | Blocking | Recovery test |

## 8. Governance, ethics and equity

| ID | Criterion | Class | Required evidence |
|---|---|---|---|
| V1-GOV-01 | Community/harm perspective is represented in agent-panel advice and owner decisions over priorities, acceptable use, interpretation and release framing | Blocking | Panel contract, findings, dissent and owner decisions |
| V1-GOV-02 | Methods, rights/data-use and country-node perspectives are assigned to agent-panel roles; controlled-node policy remains custodian-defined if activated | Blocking | Panel role contract and bounded-scope records |
| V1-GOV-03 | Conflicts, authorship, corrections, complaints, appeals and funder independence are operational | Blocking | Policies plus at least one tabletop test |
| V1-GOV-04 | The single-developer agent-panel operating model and its limitations are disclosed | Blocking | ADR-0009 and release limitations |
| V1-GOV-05 | Indigenous Data Sovereignty and CARE-aligned authority are implemented where relevant | Blocking | Node terms and governance review |
| V1-GOV-06 | At least one LMIC-led or otherwise underserved-population node participates before unqualified global claims | Blocking for global claim | Node agreement and leadership evidence |
| V1-GOV-07 | Outputs assess plausible harms, stigma, inequity and misuse | Blocking | Acceptable-use and harm review |

## 9. Documentation, accessibility and user success

| ID | Criterion | Class | Required evidence |
|---|---|---|---|
| V1-DOC-01 | Quickstart, user, developer, methods, node-operator, data-steward and release guides are complete | Blocking | Documentation inventory and link check |
| V1-DOC-02 | Every runnable example is tested as documentation | Blocking | Documentation test results |
| V1-DOC-03 | Diagrams and visual outputs have accessible text alternatives; colour is not the sole signal | Blocking | Accessibility review |
| V1-DOC-04 | Role-separated usability agents exercise the reference workflow and the owner dispositions their findings | Blocking | Hash-bound usability panel report and owner disposition |
| V1-DOC-05 | Citation, licence, provenance, limitations and correction instructions accompany each release | Blocking | Release inspection |

## 10. Release, adoption and sustainability

| ID | Criterion | Class | Required evidence |
|---|---|---|---|
| V1-REL-01 | The release includes source, Git history, checksums, citation metadata and a provenance-rich research object | Blocking | Release manifest and archive |
| V1-REL-02 | The public API/data package is versioned and generated from reviewed release artefacts rather than mutable working data | Blocking | Release pipeline evidence |
| V1-REL-03 | Two clean release-candidate builds and one separately executed owner-operated reproduction produce equivalent reviewed outputs | Blocking | Verification records |
| V1-SUS-01 | Primary and privacy-preserving backup operational roles have recorded scope and acceptance | Blocking | Owner roster, acceptance and handoff evidence |
| V1-SUS-02 | Infrastructure, node support and release costs have a funded or institutionally committed operating model | Blocking | Approved sustainability plan |
| V1-SUS-03 | A contribution, succession and deprecation pathway exists if the founding maintainer withdraws | Blocking | Governance and support policies |
| V1-SUS-04 | Partner-facing claims distinguish confirmed relationships from invitations or proposals | Blocking | Communications review |

## Final release decision

The v1.0 release decision must contain:

1. the commit and release-candidate identifiers reviewed;
2. the completed criterion table with linked evidence;
3. all accepted residual risks and their owners;
4. agent-panel recommendations across methods, community/harm, rights/data-use, engineering and security, plus the repository-owner disposition;
5. a clear statement of geographic, disease and analytic scope;
6. rollback and correction instructions;
7. the final decision: **release**, **release with bounded exclusions**, **revise**, or **stop**.

A bounded exclusion must remove the unsupported capability from the v1 product promise; it cannot merely hide an unmet criterion in the limitations section.
