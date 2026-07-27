# Strategy

**Status:** Founding strategy v0.1  
**Horizon:** July 2026 to June 2031

## Strategic objective

Build the independent global measurement infrastructure required to estimate and explain the collective health, social and economic burden of rare diseases, including rare aetiologies hidden inside common diagnostic categories.

## Strategic diagnosis

The constraint is not a complete absence of data. It is that useful evidence is dispersed across incompatible classifications, disease-specific studies, registries, genomic cohorts, health-administrative systems, patient surveys and broad burden categories. Access conditions range from open download to secure analysis. No single source contains all of prevalence, severity, mortality, diagnostic delay, resource use, costs, family consequences and equity.

The programme should therefore not begin by asking for every underlying record. It should begin by defining the estimands and assembling the largest defensible public evidence layer, then make small, parameter-specific requests where public evidence is inadequate.

## Strategic choice

> **Build a federated measurement system, not a central data lake. Link estimates, not identities.**

Public and licensed aggregate sources can be ingested into an open evidence layer. Controlled datasets can be analysed through their normal secure processes. Registries and country nodes can run common code locally and return approved, disclosure-controlled parameter estimates. These components can be combined analytically without requiring the same individuals to be linked across every source.

## Theory of change

If the programme creates common definitions, transparent source metadata, portable analytic protocols and trusted governance, then data custodians can contribute comparable evidence with lower legal and operational friction. If those contributions are combined with public population and burden envelopes using explicit uncertainty and double-counting controls, then rare-disease burden can become visible and decision-relevant. If the outputs are co-governed by affected communities and translated into country and policy products, then the evidence can influence priorities, services, research and investment.

## Six strategic pillars

### 1. Define and harmonise

Create a versioned rare-disease inclusion framework and crosswalk among ORPHAcodes/ORDO, ICD-10/11, SNOMED CT, MONDO, OMIM, HPO and relevant national coding systems. Define aggregation rules and disease hierarchies designed specifically for burden estimation.

### 2. Measure population-health burden

Estimate prevalence, incidence, mortality, years of life lost, years lived with disability and disability-adjusted life years where defensible. Report observed and modelled values separately and propagate uncertainty.

### 3. Reveal rare within common

Estimate the proportion and distinct severity profile of rare aetiologies within common categories such as diabetes, bronchiectasis, epilepsy, cardiomyopathy and chronic kidney disease. Avoid assuming that a prevalence fraction is also a DALY fraction.

### 4. Quantify economic and social burden

Measure healthcare use, direct medical and non-medical costs, caregiver time, education effects, labour-market consequences, catastrophic expenditure and distributional impact. Declare analytic perspective and price-year assumptions.

### 5. Build the federated evidence commons

Publish a data-asset catalogue, common metadata and quality standards, reproducible reference code, node execution packages and disclosure-safe output specifications. Sensitive records remain in approved environments.

### 6. Translate evidence into decisions

Produce a global atlas, annual report, country profiles, diagnostic-gap analyses, policy indicators, HTA inputs and investment cases. Outputs must explain limitations and actionable implications, not merely rank countries or diseases.

## Flagship products

1. **Global Rare Disease Burden Atlas and Report** — collective burden, uncertainty, coverage and gaps.
2. **Rare Within Common Observatory** — attributable fractions and outcome differences for selected common disease envelopes.
3. **Diagnostic Journey and Delay Atlas** — diagnosis, misdiagnosis and treatment consequences where data permit.
4. **Rare Disease Economic and Social Burden Accounts** — health-system, household and societal perspectives.
5. **Data and Methods Commons** — ontologies, metadata, protocols, code, decision records and quality grades.

## Initial demonstrators

### Monogenic diabetes within diabetes

Tests disease attribution, diagnostic delay, treatment change, complication profiles, genomic ascertainment and economic value.

### Rare aetiologies within bronchiectasis

Tests multi-aetiology attribution, overlapping diagnoses and the need to distinguish causal subgroups from syndromic burden.

### Collective paediatric rare-disease burden

Tests linked administrative definitions, mortality, healthcare use, cost, diagnostic pathways and international replication, beginning with an Australian proof and a separately governed New Zealand or other country node.

## Operating model

### Core commons

A small central team maintains definitions, schemas, provenance, reference code, release processes and policy translation.

### Country and thematic nodes

Locally led teams use national or disease-specific data under local governance. Nodes contribute metadata, quality assessments and approved aggregate estimates.

### Methods and patient governance

A Scientific Methods Council and a Patient and Community Council jointly oversee priorities, acceptable use, interpretation and release. A Data Governance and Ethics Committee reviews privacy, licences and cross-border constraints.

### Independent assurance

External review, reproducibility checks, conflict declarations and a transparent correction policy protect credibility.

## Partnership strategy

Approaches should be parameter-specific and institution-appropriate:

- burden organisations: methods, cause hierarchy, public estimates and validation;
- ontology and standards organisations: crosswalks and version governance;
- genomic cohorts: phenotype-genotype fractions and outcome profiles in secure environments;
- administrative data custodians: utilisation, mortality, costs and diagnostic pathways;
- registries: disease-specific natural history and locally observed parameters;
- patient organisations: priorities, governance and lived-experience measures;
- funders and conveners: shared infrastructure, country-node grants and policy adoption.

No organisation should be asked initially for unrestricted transfer of all underlying data.

## Funding proposition

The investment case is for shared measurement infrastructure and distributed analytic capacity, not a one-off disease study. A blended portfolio could include philanthropic seed funding, public research grants, institutional co-investment and ring-fenced node grants. Industry funding, if accepted, should be pooled and non-controlling, with public conflict declarations.

## Delivery sequence to stable v1.0

The implementation sequence is controlled by `conductor/roadmap.yml` and the detailed roadmap in `docs/roadmap-v1.md`. Progress is gate-based rather than date-driven.

| Release stage | Strategic outcome |
|---|---|
| Foundation and programme control | Founding proposition, complete track portfolio, maturity model and stable-release contract |
| Public evidence foundation | Reproducible public-source acquisition and demonstrated novelty/complementarity |
| Semantic and evidence core | Versioned disease hierarchy, mappings and parameter ledger |
| Public burden methods | Tested estimation and uncertainty engine plus first rare-within-common demonstrator |
| Federated and multi-method validation | Portable node runner, second rare-within-common analysis and controlled-data-ready paediatric methods |
| Economic, gap and atlas beta | Economic/social methods, evidence-gap map and accessible reviewed aggregate products |
| Governance and operational hardening | Constituted decision rights, security, reliability, support and sustainable ownership |
| Stable v1 | Independent reproduction, complete documentation and formal multi-lane release decision |

A polished atlas cannot substitute for missing semantic, provenance or validation gates. Each release may narrow its supported scope when the evidence does not justify the broader claim.

## Initial mobilisation priorities

- confirm the working scope, name and institutional-host options;
- recruit a patient/community co-lead with real decision rights;
- publish the programme-control repository and stable-release principles;
- complete the adjacency, duplication and novelty assessment;
- select and freeze the first demonstrator estimands;
- verify the first public-source access and licence contracts;
- identify one secure genomic and one administrative-data route without treating access as confirmed;
- prepare a bounded case for support tied to the track portfolio and decision gates.

## Measures of progress

### Foundation and public-data readiness

- all v1-critical tracks have valid specifications, dependencies and owners;
- the source and release catalogue distinguishes public, registered, controlled, federated and new collection routes;
- the novelty review records a proceed, narrow, combine, revise or stop decision;
- the first acquisition-to-normalised-table workflow reproduces from a clean environment.

### Scientific and platform readiness

- the semantic hierarchy and parameter ledger are versioned and tested;
- expected affected-population and rare-aetiology methods propagate uncertainty and reject incompatible operations;
- three demonstrator protocols exercise different evidence and overlap structures;
- a synthetic federated node and at least one approved local pilot validate the node contract;
- the gap map makes missing public evidence and additional custodian asks explicit.

### Stable-release readiness

- all blocking criteria in `docs/v1-acceptance-criteria.md` have linked evidence;
- at least one released analysis is independently reproduced;
- patient/community, scientific, data-governance, engineering and security authorities approve the supported scope;
- release, correction, migration, support and succession processes are tested;
- geographic and global claims are bounded to represented evidence and governance.

## Strategic risks and responses

| Risk | Response |
|---|---|
| Perceived duplication | Publish adjacency analysis and define the measurement-layer role narrowly |
| Data access delays | Deliver a useful public-data MVP before controlled access completes |
| High-income bias | Fund LMIC-led nodes and grade transportability explicitly |
| Double counting | Use ontology-aware mutually exclusive aggregation and overlap sensitivity analysis |
| False precision | Publish uncertainty, quality grades and non-estimable categories |
| Custodian reluctance | Request specific parameters or local code execution, not unrestricted data transfer |
| Commercial influence | Pool funding, separate governance and disclose conflicts |
| Founder dependence | Establish co-leadership, institutional hosting and documented succession early |
