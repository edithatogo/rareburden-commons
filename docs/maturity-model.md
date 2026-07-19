# RareBurden Commons maturity model

## Purpose

The maturity model prevents the programme from equating a larger codebase or a polished atlas with a mature scientific product. It provides a common scale for judging scientific, data, engineering, governance and operational readiness.

## Levels

| Level | Name | Meaning |
|---|---|---|
| **0** | Concept | A need or method is described but not specified or tested |
| **1** | Foundation | Requirements, architecture and protocol exist; implementation is partial |
| **2** | Repeatable alpha | A maintained workflow runs on lawful fixtures with provenance and automated tests |
| **3** | Validated beta | Independent data or users test the workflow; limitations and failure modes are characterised |
| **4** | Release candidate | Interfaces are frozen, governance and operations are active, and blocking findings are closed |
| **5** | Stable | The capability is supported, independently reproducible, monitored, versioned and sustainably owned |

## Current baseline after v0.2.0

| Dimension | Baseline | Evidence | Principal gap to v1.0 |
|---|---:|---|---|
| Product and strategy | 2 | Vision, strategy, requirements and complete track portfolio | External validation of priorities and durable ownership |
| Scientific methods | 1 | Umbrella protocol and conceptual architecture | Executable estimands, demonstrators, independent review and validation |
| Data acquisition and provenance | 1 | Source catalogue and schema | Working adapters, source-release manifests and licence-tested pipelines |
| Semantic interoperability | 0–1 | Standards identified | Versioned burden hierarchy, mappings and overlap tests |
| Evidence and parameter management | 0–1 | Ledger described in protocol | Machine-readable ledger, quality and transportability implementation |
| Burden modelling | 0 | Formulae and requirements only | Tested engine, uncertainty propagation and reference analyses |
| Federated/privacy-preserving execution | 0–1 | Trust boundaries and sequence design | Portable runner, synthetic validation and approved-node pilot |
| Software quality | 1–2 | Small tested validator and CI | Broader implementation, type safety, coverage, compatibility and performance |
| Security and operations | 1 | Repository safety rules and basic CI | Threat model, SBOM, signing, monitoring, recovery and support |
| Governance and equity | 1 | Proposed principles and bodies | Constituted decision rights, patient remuneration, country and Indigenous governance |
| Documentation and usability | 1 | Foundational technical and programme documents | Role-based guides, tutorials, accessibility testing and external user validation |
| Adoption and sustainability | 0–1 | Intended users and funding concept | External nodes, maintainers, institutional host, support and financing model |

The baseline is intentionally conservative. Documentation describing a future capability does not move that capability beyond Level 1.

## v1.0 maturity target

A stable v1.0 requires:

- no blocking dimension below **Level 4**;
- scientific methods, provenance, software quality, security/release engineering and documentation at **Level 5** for the supported v1 scope;
- governance, adoption and sustainability at least **Level 4**, with named owners and tested procedures;
- every exception documented as a bounded non-goal rather than an unacknowledged deficiency.

## Dimension-specific evidence

### Product and strategy

**Level 5 evidence:** supported and unsupported use cases are explicit; release scope is stable; user outcomes have been tested with representative users; change control is active; roadmap ownership is named.

### Scientific methods

**Level 5 evidence:** protocol family is versioned; estimands are machine-readable; overlap and uncertainty algorithms are tested; three demonstrators have documented validation; independent scientific review and reporting checklists are complete.

### Data acquisition and provenance

**Level 5 evidence:** supported source releases can be acquired or registered reproducibly; manifests and checksums are complete; licence restrictions are enforced; source changes fail safely; lineage reaches every public output.

### Semantic interoperability

**Level 5 evidence:** disease definitions, mappings and burden hierarchy are versioned; ambiguous mappings remain explicit; parent-child and multi-diagnosis overlap tests pass; schema migrations and ontology diffs are supported.

### Evidence and parameter management

**Level 5 evidence:** every estimate resolves to parameter records with source, quality, uncertainty, transportability and assumption status; invalid or incomplete evidence cannot enter a release.

### Burden modelling

**Level 5 evidence:** deterministic and simulation paths are tested; convergence, sensitivity and structural uncertainty are reported; unsupported operations are rejected; reference analyses reproduce from release artefacts.

### Federated and privacy-preserving execution

**Level 5 evidence:** a portable node package runs offline, records its environment, applies local disclosure rules and produces schema-valid exports; independent custodians have executed it successfully; withdrawal and correction procedures have been tested.

### Software quality

**Level 5 evidence:** supported runtimes pass unit, integration, contract, property, statistical and end-to-end tests; critical modules meet coverage thresholds; APIs and schemas follow compatibility policy; performance budgets are met.

### Security and operations

**Level 5 evidence:** threat model, secret scanning, dependency controls, SBOM, signed release, build provenance, incident response, backup/recovery and supported-version policy are tested and owned.

### Governance and equity

**Level 5 evidence:** patient/community and scientific governance have documented voting rights; conflicts and acceptable use are enforced; country-node and Indigenous data-governance rights are operational; decisions and minutes are transparent.

### Documentation and usability

**Level 5 evidence:** user, developer, methods, node-operator and release guides are complete; examples run as written; accessible alternatives exist; independent users complete key workflows without maintainer intervention.

### Adoption and sustainability

**Level 5 evidence:** more than one institution can operate the supported workflow; maintainers and succession are documented; infrastructure costs and funding are covered; release and support duties have durable ownership.

## Assessment process

At each release candidate:

1. each assurance lane scores every dimension and cites evidence;
2. disagreements and exceptions are recorded rather than averaged away;
3. the lowest blocking score determines readiness;
4. remediation tasks are added to the relevant track;
5. the assessment is committed with the release decision.

A maturity score is an assurance aid, not a marketing metric. It must never be used to hide scientific uncertainty or compare countries.
