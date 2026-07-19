# Roadmap to a stable RareBurden Commons v1.0

**Roadmap baseline:** v0.2  
**As of:** 19 July 2026  
**Target stable release:** v1.0.0, gate-driven with an indicative window of 2030 Q2

## 1. Purpose of this roadmap

This roadmap converts the founding concept into a delivery system for a stable, supportable and independently reviewed v1.0. It is deliberately more demanding than a conventional software roadmap because RareBurden Commons must mature simultaneously as:

- scientific measurement infrastructure;
- a reproducible data and software product;
- a federated collaboration pattern for controlled health data;
- a public-interest governance system;
- a policy-facing evidence product.

Dates are planning assumptions, not permission to weaken standards. A release moves when an entry or exit criterion is not met.

## 2. What “stable v1.0” means

V1.0 will be considered stable when the **contracts and release process** are dependable, not when every rare disease and country has a definitive estimate. Stability requires:

1. a versioned burden-purpose disease hierarchy and mapping workflow;
2. reproducible acquisition and provenance for the initial public sources;
3. machine-readable evidence, parameter, assumption and analysis contracts;
4. tested population, rare-aetiology, uncertainty and overlap methods;
5. three independently reviewed demonstrators;
6. a disclosure-safe federated node package tested across multiple locally governed environments;
7. operational patient/community, scientific and data-governance decision rights;
8. accessible static and machine-readable public releases with correction and support processes;
9. mature security, dependency, incident, recovery and release controls;
10. bounded claims that match actual geographic and population representation.

The normative v1 product is a versioned static release and reference command-line implementation. A hosted API may be provided, but it is not required to be the sole source of scientific truth.

## 3. V1 product boundary

### Included by v1

- public source and access catalogue with tested access states;
- source-release acquisition and registration manifests;
- semantic backbone and burden-purpose aggregation hierarchy;
- evidence and parameter ledger;
- public burden engine with uncertainty and overlap controls;
- public-data sufficiency and gap atlas;
- monogenic-diabetes, bronchiectasis and paediatric-burden demonstrators;
- federated node runner and disclosure-controlled output contract;
- economic and social burden module;
- static atlas, country profiles and machine-readable release;
- stable schemas, CLI, documentation, support and migration policy;
- independent scientific, engineering, governance and community release approval.

### Explicitly not required for v1

- definitive estimates for every rare disease and every country;
- an international participant-level data lake;
- real-time clinical surveillance or clinical decision support;
- unrestricted redistribution of source data;
- causal treatment-effect claims from ecological burden models;
- a production web service with a universal uptime guarantee;
- claims of global representativeness before the stated node and equity gates are met.

## 4. Maturity ladder

| Release | Maturity state | Core question answered |
|---|---|---|
| **v0.1** | Founding scaffold | Is the programme proposition coherent and safe enough to specify? |
| **v0.2** | Controlled roadmap | Is all work to v1 decomposed, gated, owned by role and machine-checkable? |
| **v0.3** | Public-data substrate | Can source releases be found, lawfully acquired or registered, and reproduced? Is the programme genuinely additive? |
| **v0.4** | Semantic/evidence core | Can diseases, mappings, evidence and parameters be represented without hidden ambiguity? |
| **v0.5** | Methods alpha | Can bounded public estimates and gaps be generated with defensible uncertainty and overlap handling? |
| **v0.6** | Demonstrator/node alpha | Does rare-within-common estimation work end to end, including a synthetic secure-node pathway? |
| **v0.7** | Multi-demonstrator beta | Does the method generalise across disease structures, administrative data and economic/social outcomes under real governance? |
| **v0.8** | Product/operations beta | Can reviewed evidence be released accessibly and operated securely as a coherent product? |
| **v0.9** | Release candidate | Can independent teams reproduce and challenge the frozen v1 contracts and outputs? |
| **v1.0** | Stable | Can the project support, correct, migrate and defend a bounded public release over time? |

## 5. Release train and exit gates

| Milestone | Release | Indicative window | Principal outputs | Non-negotiable exit gate |
|---|---:|---:|---|---|
| M0 | v0.1.0 | 2026 Q3 | Founding strategy, protocol, catalogue and validator | Foundation tagged and independently rechecked |
| M1 | v0.2.0 | 2026 Q3 | Full Conductor track system, v1 definition of done, quality/release/risk controls | Every v1 track specified and dependency graph validates |
| M2 | v0.3.0 | 2027 Q1 | Four reproducible source pathways and novelty/adjacency review | Source provenance works end to end; proceed/partner/narrow/stop decisions published |
| M3 | v0.4.0 | 2027 Q4 | Disease hierarchy, mappings, evidence and parameter ledger | Semantic and evidence contracts pass scientific, community and engineering review |
| M4 | v0.5.0 | 2028 Q2 | Public burden engine and gap atlas | Uncertainty, overlap, evidence status and non-estimability are explicit and tested |
| M5 | v0.6.0 | 2028 Q4 | Monogenic-diabetes demonstrator and federated node alpha | Demonstrator reproduces; synthetic node emits only approved aggregates |
| M6 | v0.7.0 | 2029 Q2 | Bronchiectasis, paediatric and economic/social modules; operational governance | Multiple environments and three demonstrators pass their defined review gates |
| M7 | v0.8.0 | 2029 Q3 | Atlas beta, machine-readable releases, security and operational controls | Full release pipeline, accessibility, threat model and recovery drills pass |
| M8 | v0.9.0 | 2030 Q1 | Frozen release candidate and independent validation | Two clean reproductions, node/equity threshold and 90-day soak pass |
| M9 | v1.0.0 | 2030 Q2 | Stable public release | Every v1 definition-of-done criterion has objective evidence or a time-limited approved exception |

The exact machine-readable release plan is maintained in `conductor/roadmap.yml`.

## 6. Track portfolio

### Programme control and discovery

- **001 Foundation and public-data protocol** — complete.
- **003 V1 roadmap and programme control** — establishes this release system and automated validation.
- **004 Landscape, adjacency, novelty and partnership map** — tests the white-space hypothesis and defines where to build, partner, narrow or stop.

### Data and semantics

- **002 Public-source acquisition and provenance adapters** — establishes lawful, versioned and reproducible inputs.
- **005 Semantic backbone and burden-purpose hierarchy** — defines disease identity, mappings, aggregation and overlap rules.
- **006 Evidence and parameter ledger** — represents evidence, assumptions, quality, transportability and lineage.

### Methods and demonstrators

- **007 Public burden engine and uncertainty** — implements core estimands, uncertainty and sensitivity methods.
- **008 Public-data gap atlas and quality grading** — exposes what can and cannot be estimated.
- **009 Monogenic-diabetes demonstrator** — first rare-within-common proof.
- **010 Bronchiectasis demonstrator** — multi-aetiology and overlap stress test.
- **011 Paediatric rare-disease burden demonstrator** — linked administrative-data and country portability test.
- **013 Economic and social burden** — health-system, household and societal consequences.

### Federated platform, trust and products

- **012 Federated node runner and disclosure control** — portable local execution and approved aggregate outputs.
- **014 Governance, equity and participation** — operational patient/community and locally governed decision rights.
- **015 Atlas, API and policy products** — accessible, machine-readable and decision-relevant releases.
- **016 Security, reliability and release engineering** — supply chain, incident, recovery, support and release evidence.
- **017 Independent validation and v1 integration** — frozen contracts, clean-room reproduction, release-candidate soak and launch decision.

## 7. Critical path

The critical path is:

> V1 programme control → public-source acquisition → semantic backbone → evidence ledger → burden engine → monogenic-diabetes proof → federated node → atlas integration → security/release hardening → independent validation.

Landscape/novelty, governance/equity and security begin early and run in parallel. They are not end-stage paperwork: each can block a scientific or public release.

## 8. Release decision model

Every milestone has four possible decisions:

- **Proceed:** exit criteria are met and the next milestone may start.
- **Proceed with bounded exception:** a non-critical criterion has an owner, expiry date and published impact assessment.
- **Revise or narrow:** the evidence supports a smaller scope or different architecture.
- **Stop or partner:** duplication, infeasibility, unacceptable risk or lack of legitimacy makes independent continuation unjustified.

Critical scientific-validity, privacy, data-rights, patient/community legitimacy or high-severity security failures cannot receive a routine exception.

## 9. Resource assumptions

The roadmap assumes a funded multidisciplinary core covering:

- programme and product leadership;
- epidemiology and burden methods;
- ontology and clinical genetics;
- health economics;
- data engineering and statistical software;
- privacy, security and federated analytics;
- patient/community and country-node participation;
- policy translation and programme operations.

A smaller unfunded team can complete public-data and methods components, but controlled-node validation, remunerated participation, translation and sustainable support require dedicated resources. The roadmap should not disguise unfunded dependencies as engineering tasks.

## 10. Stable does not mean static

After v1.0, schema and API compatibility follow the published deprecation policy. Scientific estimates continue to change with new data, ontology releases and methods. Stability means those changes are versioned, reviewable, reversible and reproducible rather than silently absorbed.
