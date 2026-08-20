# Roadmap to a stable RareBurden Commons v1.0

**Roadmap baseline:** v0.3 release-candidate
**As of:** 19 July 2026
**Target stable release:** v1.0.0, gate-driven with an indicative window of 2030 Q2

## 1. Purpose of this roadmap

This roadmap converts the founding concept into a delivery system for a stable, supportable and independently reviewed v1.0. It is deliberately more demanding than a conventional software roadmap because RareBurden Commons must mature simultaneously as:

- scientific measurement infrastructure;
- a reproducible data and software product;
- a federated collaboration pattern for controlled health data;
- a public-interest governance system;
- a policy-facing evidence product.

Dates are planning assumptions, not permission to weaken standards. A release does not advance when an entry or exit criterion is not met.

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
| **v0.3** | Public-data and scholarly-assurance substrate | Can source releases be found, lawfully acquired or registered, transformed with auditable provenance, and reproduced? Is the programme genuinely additive? |
| **v0.4** | Semantic/evidence core | Can diseases, mappings, evidence and parameters be represented without hidden ambiguity? |
| **v0.5** | Methods alpha | Can the first bounded reference analysis be generated with defensible uncertainty and overlap handling? |
| **v0.6** | Federated/multi-aetiology alpha | Can the methods run through a disclosure-safe synthetic node and a second disease structure? |
| **v0.7** | Economic/paediatric beta | Do the contracts generalise to administrative data and health-system, household and societal outcomes? |
| **v0.8** | Validated product beta | Can quality-graded evidence, gaps and aggregate outputs be released accessibly with full provenance? |
| **v0.9** | Governed release candidate | Are governance, security, reliability and operating controls ready to support a frozen candidate? |
| **v1.0** | Stable | Can independent users reproduce, operate, support, correct and migrate the bounded public release? |

## 5. Release train and exit gates

| Milestone | Release | Indicative window | Principal outputs | Non-negotiable exit gate |
|---|---:|---:|---|---|
| M0 | v0.1.0 | 2026 Q3 | Founding strategy, protocol, catalogue and validator | Foundation tagged and independently rechecked |
| M1 | v0.2.0 | 2026 Q3 | Full Conductor track system, v1 definition of done, quality/release/risk controls | Every v1 track specified and dependency graph validates |
| M2 | v0.3.0 | 2027 Q1 | Four reproducible source pathways, novelty/adjacency review and scholarly-assurance substrate | Source and transformation provenance work end to end; claims remain conservative; proceed/partner/narrow/stop decisions published |
| M3 | v0.4.0 | 2027 Q4 | Disease hierarchy, mappings, evidence and parameter ledger | Semantic and evidence contracts pass scientific, community and engineering review |
| M4 | v0.5.0 | 2028 Q2 | Public burden engine and monogenic-diabetes alpha | Deterministic and simulation analyses reproduce; unsupported operations fail safely; first demonstrator passes independent scientific review |
| M5 | v0.6.0 | 2028 Q4 | Federated node and bronchiectasis alpha | Synthetic node emits only approved aggregates; a second operator runs it; second demonstrator validates overlap handling |
| M6 | v0.7.0 | 2029 Q2 | Economic/social and paediatric beta | Economic contracts are explicit; the paediatric workflow passes synthetic linked-data and disclosure tests; claims remain bounded by approvals |
| M7 | v0.8.0 | 2029 Q3 | Quality, gap and equity assurance plus atlas/API beta | Gap maps are released; at least one analysis is independently reproduced; public outputs expose provenance, uncertainty, quality and missingness |
| M8 | v0.9.0 | 2030 Q1 | Operational governance and security/reliability release candidate | Required governance is active; threat model, locked build, SBOM, provenance and recovery exercises pass; no blocking finding remains |
| M9 | v1.0.0 | 2030 Q2 | Documentation, adoption, sustainability and stable public release | All blocking criteria have evidence; two clean builds and one independent reproduction agree; support and succession are approved |

The exact machine-readable release plan is maintained in `conductor/roadmap.yml`.

## 6. Track portfolio

### Programme control and discovery

- **[001-foundation — Foundation and public-data protocol](../conductor/archive/001-foundation/spec.md)** — archived founding scaffold.
- **[006-v1-delivery-system — v1 delivery system and foundation hardening](../conductor/archive/006-v1-delivery-system/spec.md)** — establishes this release system and automated validation.
- **[007-landscape-novelty — Landscape, adjacency, novelty and partnership map](../conductor/archive/007-landscape-novelty/spec.md)** — archives the completed bounded technical adjacency evidence and owner narrow decision without asserting comprehensive coverage, confirmed novelty or partnership.
- **[018-scholarly-provenance-reproducibility — Scholarly provenance, protocol transparency and reproducibility](../conductor/archive/018-scholarly-provenance-reproducibility/spec.md)** — archived scholarly assurance substrate distinguishing planned from executed work and packaging exact source-to-result evidence without overstating external validation.

### Data and semantics

- **[002-public-source-acquisition — Public-source acquisition and provenance adapters](../conductor/tracks/002-public-source-acquisition/spec.md)** — establishes lawful, versioned and reproducible inputs.
- **[008-semantic-backbone — Semantic backbone and burden-purpose hierarchy](../conductor/tracks/008-semantic-backbone/spec.md)** — defines disease identity, mappings, aggregation and overlap rules.
- **[009-evidence-parameter-ledger — Evidence and parameter ledger](../conductor/tracks/009-evidence-parameter-ledger/spec.md)** — represents evidence, assumptions, quality, transportability and lineage.

### Methods and demonstrators

- **[010-public-burden-engine — Public burden engine and uncertainty framework](../conductor/tracks/010-public-burden-engine/spec.md)** — implements core estimands, uncertainty and sensitivity methods.
- **[003-monogenic-diabetes-demonstrator — Monogenic diabetes rare-within-common demonstrator](../conductor/tracks/003-monogenic-diabetes-demonstrator/spec.md)** — first rare-within-common proof.
- **[011-bronchiectasis-demonstrator — Bronchiectasis rare-aetiology demonstrator](../conductor/tracks/011-bronchiectasis-demonstrator/spec.md)** — multi-aetiology and overlap stress test.
- **[005-economic-social-burden — Patient, family, economic and social burden module](../conductor/tracks/005-economic-social-burden/spec.md)** — health-system, household and societal consequences.
- **[012-paediatric-burden-demonstrator — Collective paediatric rare-disease burden demonstrator](../conductor/tracks/012-paediatric-burden-demonstrator/spec.md)** — linked administrative-data and country-portability test.

### Federated platform, trust and products

- **[004-federated-node-runner — Federated country-node execution package](../conductor/tracks/004-federated-node-runner/spec.md)** — portable local execution and approved aggregate outputs.
- **[013-quality-validation-gap-equity — Quality, validation, gap mapping and equity assurance](../conductor/tracks/013-quality-validation-gap-equity/spec.md)** — exposes what can and cannot be estimated and constrains representation claims.
- **[014-atlas-api-release — Atlas, API and reproducible release engineering](../conductor/tracks/014-atlas-api-release/spec.md)** — accessible, machine-readable and decision-relevant releases.
- **[015-governance-partnership-policy — Operational governance, partnerships and policy translation](../conductor/tracks/015-governance-partnership-policy/spec.md)** — operational patient/community, scientific and locally governed decision rights.
- **[016-security-reliability-operations — Security, reliability, performance and operations](../conductor/tracks/016-security-reliability-operations/spec.md)** — supply chain, incident, recovery, performance, support and release evidence.
- **[017-documentation-adoption-v1 — Documentation, adoption, sustainability and stable v1 release](../conductor/tracks/017-documentation-adoption-v1/spec.md)** — independent usability, reproduction, support, succession and launch decision.

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
