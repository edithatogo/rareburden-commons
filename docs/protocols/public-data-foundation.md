# Public-data foundation and federated extension protocol

**Protocol identifier:** RBC-P001  
**Version:** 0.1.0  
**Status:** Founding draft; not yet externally peer reviewed or preregistered  
**Date:** 18 July 2026  
**Planned registration:** OSF or equivalent before numerical primary analyses

## 1. Title

A public-data-first, federated protocol to estimate the collective health, social and economic burden of rare diseases and rare aetiologies within common disease categories.

## 2. Rationale

No single dataset contains all information required to measure rare-disease burden. Disease knowledge, epidemiology, population denominators, disability, mortality, diagnostic delay, healthcare use, genomic attribution, costs and household consequences reside in different systems with different access conditions. The protocol therefore treats burden estimation as a structured synthesis of versioned parameters rather than an attempt to construct a universal patient-level dataset.

The first stage will establish what can be estimated from public data and where uncertainty or non-estimability remains. Controlled and partner-held data will be added through approved secure or federated analyses targeted at specific missing parameters.

## 3. Aims

### Primary aim

Develop a reproducible framework for estimating the collective burden of rare diseases while preventing double counting and exposing uncertainty, data quality and geographic inequity.

### Secondary aims

1. Catalogue international data sources and their practical access routes.
2. Construct a versioned burden-purpose rare-disease definition and hierarchy.
3. Estimate expected affected populations using public epidemiology and denominators.
4. Develop methods for rare-aetiology attribution within common disease envelopes.
5. Specify health, economic and social burden modules.
6. Define a portable federated analysis contract for controlled country and cohort nodes.
7. Identify which conclusions cannot be supported without additional data.

## 4. Research questions

1. What rare-disease burden components can be estimated reproducibly from public data alone?
2. Which diseases, countries, ages and outcomes are systematically missing or weakly measured?
3. How can disease-level estimates be aggregated without double counting overlapping syndromes, subtypes and causal pathways?
4. What proportion of selected common disease categories is plausibly attributable to rare aetiologies, and how does their severity profile differ?
5. What minimum additional parameters must be requested from controlled datasets, registries or new patient/family collections?
6. How sensitive are results to disease definitions, evidence quality, transportability and ascertainment?

## 5. Study design

A modular evidence-synthesis and burden-modelling study with four linked components:

1. **semantic and source foundation:** disease definitions, coding crosswalks, source register and evidence ledger;
2. **public-data analyses:** epidemiology, population denominators, burden envelopes and health-system context;
3. **federated extensions:** controlled, registry or country analyses executed under local governance;
4. **translation:** reviewed aggregate releases, gap maps, country profiles and policy products.

No central participant-level cohort will be assembled under this protocol.

## 6. Scope

### Population

People of any age living with a condition meeting the protocol's rare-disease definition, including people who are undiagnosed or coded under a broader common condition where a rare aetiology can be estimated.

### Geography

Global in aspiration. Estimates will only be described as global when source coverage, modelling and validation justify that label. Country and regional outputs will carry evidence and transportability grades.

### Time

The primary reference year will be selected per release based on availability across population, epidemiology and burden sources. Historical trends may be included when definitions remain sufficiently comparable.

### Outcomes

- prevalence and incidence;
- deaths and mortality rates;
- years of life lost, years lived with disability and DALYs where defensible;
- diagnostic delay, misdiagnosis and treatment change;
- healthcare utilisation and direct medical expenditure;
- direct non-medical, household, caregiver, education and productivity consequences;
- equity and distributional outcomes.

### Exclusions for the first release

- individual clinical decision support;
- variant pathogenicity reclassification;
- causal treatment-effect estimation without an appropriate design;
- public release of controlled or participant-level data;
- burden estimates based solely on unvalidated automated text extraction.

## 7. Key definitions

### Rare disease

The operational definition will be versioned and jurisdiction-aware. The primary semantic backbone will use ORPHAcodes/ORDO, with mappings to other systems. The protocol will preserve the source jurisdiction's threshold and definition rather than force one prevalence threshold into all legal contexts.

### Disease entity

A defined disorder, group of disorders, subtype, aetiology or syndrome node with a stable project identifier and explicit inclusion/exclusion rule.

### Rare within common

A rare genetic, developmental, metabolic, immunological or other aetiology represented within a broad common diagnosis or syndrome. Attribution requires an explicit denominator and mutually interpretable case definitions.

### Evidence status

- **Observed:** directly measured in the stated population.
- **Derived:** transformed from observed data using transparent arithmetic or coding.
- **Modelled:** estimated using a statistical model combining multiple inputs.
- **Transferred:** borrowed from another population with an explicit transport model or assumption.
- **Assumed:** expert or scenario input used because adequate empirical evidence is unavailable.

## 8. Disease inclusion and hierarchy

### Inclusion process

1. Freeze the selected ontology release.
2. Define eligible entity types and exclusions.
3. Assign each entity to a burden-purpose hierarchy.
4. Identify parent-child, subtype, syndrome, aetiology and manifestation relationships.
5. Mark nodes that are mutually exclusive, overlapping or non-additive.
6. Map to burden and administrative coding systems with mapping confidence.
7. Obtain clinical, ontology and patient/community review before release.

### Aggregation rule

Only mutually exclusive leaf or analysis nodes may be summed directly. Where overlap exists, the analysis must use one of:

- a mutually exclusive reclassification;
- observed joint distributions;
- inclusion-exclusion methods;
- probabilistic overlap modelling;
- scenario bounds;
- a declaration that the aggregate is non-estimable.

### Versioning

Every analysis records ontology release, project hierarchy version, mapping version and any manual adjudications. Changes that alter inclusion or aggregation require a decision record and sensitivity analysis where feasible.

## 9. Data sources and access

Sources will be selected from the machine-readable register and assigned an access class:

- open download/API;
- public web or routine registration;
- controlled research;
- federated partner;
- new collection.

The public-data phase may use only data for which access, licence and permitted reuse are documented. Controlled-data extensions require local approvals and a node-specific appendix.

## 10. Source eligibility

### General inclusion criteria

A source must provide or support at least one defined parameter and have sufficient metadata to identify population, period, case definition, unit and provenance.

### Epidemiological sources

Eligible designs may include population registries, screening studies, linked administrative analyses, representative surveys, systematic reviews and disease-specific cohorts. Referral-centre series may inform natural history or severity but will not be treated as population prevalence without adjustment.

### Burden envelopes

WHO, IHME or national burden estimates may provide broad cause totals. Each envelope's cause hierarchy, metric, age/sex structure, year, uncertainty and licence must be recorded.

### Genomic and phenotype sources

Public knowledge bases inform definitions and variant/disease relationships. Cohort-derived prevalence or attributable fractions require ascertainment, ancestry, penetrance, phenotype and technical-coverage assessment.

### Economic sources

Eligible data include national expenditure aggregates, linked administrative costing, claims, registries, surveys and published micro-costing. Analytic perspective, currency, price year, conversion and discounting must be explicit.

## 11. Evidence and parameter ledger

Each parameter record will contain at least:

- unique parameter identifier;
- estimand and unit;
- disease-definition identifier;
- numerator and denominator definitions;
- geography, population, age, sex and period;
- source release and access class;
- observed/derived/modelled/transferred/assumed status;
- point estimate and uncertainty representation;
- sampling and ascertainment method;
- bias, quality and transportability judgements;
- overlap and double-counting notes;
- transformation code and Git commit;
- reviewer and approval status.

Values without required provenance will not enter primary analyses.

## 12. Primary estimands

### 12.1 Expected affected population

For disease or mutually exclusive group `d`, country `c`, age `a`, sex `s` and year `t`:

\[
N_{d,c,a,s,t} = P_{c,a,s,t} \times \pi_{d,c,a,s,t}
\]

where `P` is the population denominator and `π` is the prevalence. Both inputs and their uncertainty are versioned. Where prevalence is transferred across countries, the transfer model and covariates must be explicit.

### 12.2 Rare-within-common attributable population

For rare aetiology `r` within common envelope `k`:

\[
N_{r\mid k,c,a,s,t} = N_{k,c,a,s,t} \times f_{r\mid k,c,a,s,t}
\]

where `f` is an attributable case fraction. This case fraction must not automatically be applied to deaths, YLDs, DALYs or costs. Outcome-specific fractions or separate severity-state models are required when rare and non-rare subgroups differ.

### 12.3 Health loss

Where compatible severity and disability information exists:

\[
YLD_{d} = \sum_h Prev_{d,h} \times DW_h
\]

\[
YLL_{d} = \sum_x Deaths_{d,x} \times LE_x
\]

\[
DALY_{d} = YLD_{d} + YLL_{d}
\]

Health-state definitions, disability weights, comorbidity correction and standard life expectancy must be documented. A prevalence estimate alone is insufficient to infer YLDs.

### 12.4 Economic burden

Economic analyses will report components separately before aggregation:

\[
Cost_{societal} = Cost_{health} + Cost_{social\ care} + Cost_{household} + Productivity\ loss + Education\ effects
\]

Perspective-specific totals will not be mixed. Transfer payments will be handled according to the declared perspective. Currency conversion, purchasing-power adjustment, price year and discount rate will be stated.

## 13. Statistical analysis

### Descriptive public-data analysis

The first release will summarise source coverage, access class, geography, age, disease group, period, evidence status and missingness. It will not impute an all-disease global total merely to fill gaps.

### Evidence synthesis

Meta-analysis may be used when case definitions and populations are sufficiently comparable. Random-effects structure, transformations and heterogeneity measures will be specified per parameter family. When pooling is inappropriate, estimates will be presented separately or as bounded scenarios.

### Transportability

Transferred parameters will consider epidemiologically relevant moderators such as age, sex, ancestry, diagnostic capacity, consanguinity, survival, health-system access and calendar period. The model may use hierarchical partial pooling, calibration or scenario factors. Directly observed local evidence takes precedence where quality is adequate.

### Uncertainty

Uncertainty will be propagated by analytic calculation, simulation or posterior sampling as appropriate. Primary outputs should include intervals and identify uncertainty from sampling, source heterogeneity, mapping, transfer, overlap and model assumptions. Structural uncertainty will be represented through sensitivity analyses rather than hidden in a single interval.

### Missingness

Missing data will be classified as:

- not sought;
- source absent;
- source inaccessible;
- definition incompatible;
- quality inadequate;
- legally non-exportable;
- analytically non-estimable.

These categories are outputs in their own right. Multiple imputation will only be used when its assumptions are plausible and documented.

### Small numbers

Public outputs will follow source and node disclosure rules. Suppression, aggregation, rounding, interval widening or non-release may be required. The absence of a released cell must not be interpreted as zero burden.

## 14. Quality, bias and transportability assessment

Each parameter will receive domain judgements rather than a single opaque score:

1. case-definition validity;
2. population representativeness;
3. ascertainment completeness;
4. measurement reliability;
5. temporal relevance;
6. geographic transportability;
7. overlap/double-counting risk;
8. uncertainty completeness;
9. conflict-of-interest risk;
10. reproducibility and access transparency.

Judgements are High, Moderate, Low, Very low or Not assessable, with reasons. Overall use in primary analysis must be rule-based and reviewable.

## 15. Validation

Validation will use one or more of:

- comparison with independent national or registry estimates;
- hold-out countries or sources;
- known high-ascertainment populations;
- internal consistency across prevalence, incidence, mortality and survival;
- comparison of coding-based and genomically informed definitions;
- posterior predictive or simulation checks;
- expert and patient/community review of plausibility and interpretation.

Disagreement will not automatically be averaged. The source of discrepancy will be investigated and, where unresolved, shown explicitly.

## 16. Equity analysis

Where data permit, analyses will stratify by age, sex, geography, Indigenous status or ethnicity under appropriate governance, socioeconomic position, remoteness and health-system access. Categories must be locally meaningful and not exported across settings uncritically. Equity analyses will consider both burden and evidence availability.

## 17. Demonstrator modules

### Monogenic diabetes

Primary denominator: people meeting the selected diabetes definition. Parameters include monogenic fraction, diagnostic delay, treatment change, severity, complications, utilisation, costs and family consequences. Analyses will distinguish referral/genomic cohort ascertainment from population estimates.

### Bronchiectasis

Parameters include rare aetiologies such as cystic fibrosis, primary ciliary dyskinesia and immunodeficiency, with explicit handling of overlapping diagnoses and different common-envelope definitions.

### Collective paediatric burden

Defines a mutually reviewable paediatric rare-disease cohort or set of coding algorithms and tests mortality, admissions, bed-days, costs and diagnostic pathways in a controlled linked-data environment. Country implementations remain separate and locally governed.

Each demonstrator will have a prespecified appendix before analysis.

## 18. Ethics and governance

Public aggregate and knowledge-base work may not require human-research approval in every jurisdiction, but local determination will be documented. Controlled analyses require all applicable ethics, custodian and institutional approvals. Patient/community representatives will review acceptable uses, priority outcomes and public framing.

The project will not attempt re-identification, bypass access controls, or combine aggregate outputs to infer prohibited small cells. Data contributor conditions and withdrawal/correction processes will be honoured.

## 19. Reproducibility

For every release, the project will archive:

- protocol and amendments;
- disease hierarchy and mappings;
- source register and permissible aggregate inputs;
- schemas and parameter ledger;
- transformation and analysis code;
- software environment specification;
- tests and validation results;
- model diagnostics and sensitivity analyses;
- release manifest, licence notes and Git commit;
- limitations, conflicts and correction history.

Where a source cannot be redistributed, the archive will contain metadata, acquisition instructions, checksums where permitted and a reproducible query specification.

## 20. Protocol deviations and amendments

Deviations are logged with date, reason, affected analyses and decision owner. Changes to primary estimands, disease inclusion, hierarchy, main model or release criteria require a version increment and decision record. Post hoc exploratory analyses are labelled as such.

## 21. Release gates

A numerical output may be publicly released only when:

1. the estimand and disease definition are frozen;
2. source access and licence are documented;
3. evidence status and uncertainty are complete;
4. overlap and double-counting have been addressed;
5. scientific and patient/community interpretation reviews are complete;
6. disclosure and data-governance approval is documented;
7. code, metadata and permitted inputs reproduce the result;
8. limitations and non-estimable elements are visible.

## 22. Planned first outputs

1. Rare-disease source and access catalogue alpha.
2. Disease-definition and coding-gap prototype.
3. Public-data feasibility and missingness atlas.
4. Monogenic-diabetes demonstrator specification and public parameter review.
5. Federated node package contract.
6. Two-page policy and funding case grounded in the demonstrator results.

## 23. Reporting

Reporting will follow relevant observational, systematic-review, economic-evaluation, prediction-model and routine-data guidance as applicable to each module. Because this programme crosses study types, each release will state which reporting standards were applied rather than claim compliance with a single checklist.

## 24. Current limitations of this draft

This is a founding protocol. The disease inclusion framework, patient acceptable-use principles, quality rubric thresholds, primary reference year, economic perspective and demonstrator-specific analysis plans require external co-design and formal approval before primary numerical analyses.

## 25. Protocol family and stable-v1 implementation

RBC-P001 remains the umbrella protocol. Stable v1 requires demonstrator and method modules that are narrower, executable and reviewed:

- **RBC-P001A:** semantic inclusion, coding and aggregation;
- **RBC-P001B:** epidemiology and expected affected population;
- **RBC-P001C:** rare-aetiology composition within common conditions;
- **RBC-P001D:** economic and social burden;
- **RBC-P002:** monogenic-diabetes demonstrator;
- **RBC-P003:** bronchiectasis demonstrator;
- **RBC-P004:** collective paediatric administrative-data demonstrator.

These modules are owned by Tracks 003, 005, 008, 010, 011 and 012. They must define machine-readable estimands, primary and sensitivity models, validation, reporting tables and release evidence. This umbrella draft is not sufficient on its own to authorise a numerical v1 release.
