# Requirements baseline

**Status:** v0.2 planning baseline for the route to stable v1.0  
**Prioritisation:** MoSCoW — Must, Should, Could, Won't for the current programme increment. The original request's “MoWCoW” is interpreted as the standard MoSCoW method.

## Product increment

This baseline preserves the original MoSCoW product requirements and now feeds the complete release train through v1.0. Individual tracks own implementation evidence; `docs/requirements-traceability.md` maps each requirement to those tracks. The detailed stable-release contract is `docs/v1-acceptance-criteria.md`.

## Personas and decisions supported

| Persona | Decision the product should support |
|---|---|
| Patient/community leader | Where is burden visible, missing or misrepresented, and which evidence gaps deserve priority? |
| Health ministry or public agency | What is the plausible national burden and which service or data investments are justified? |
| Researcher or registry lead | Which definitions, sources and methods permit a comparable analysis? |
| Data custodian | What exact parameter is requested, under which governance and disclosure rules? |
| Funder | What shared infrastructure or node investment would reduce a material evidence gap? |
| Burden-methods team | How can rare causes be incorporated without overlap, hierarchy or severity errors? |

## Must have

### Scientific definition and scope

- **M-01:** Maintain a versioned inclusion framework for rare diseases, disease groups and rare-within-common aetiologies.
- **M-02:** Record the ontology, coding-system and release version used for every disease definition.
- **M-03:** Define the estimand before analysis, including population, geography, age, sex, period, outcome and perspective.
- **M-04:** Distinguish directly observed values, literature-derived parameters, transformed data, modelled estimates and expert assumptions.
- **M-05:** Implement explicit overlap and double-counting rules; simple summation across non-exclusive diseases is prohibited.
- **M-06:** Carry uncertainty through transformations and report it with estimates.

### Source and access management

- **M-07:** Maintain a machine-readable source register with custodian, geography, access class, licence, version, retrieval date, purpose and limitations.
- **M-08:** Classify sources as open download/API, public web/registration, controlled research, federated partner or new collection.
- **M-09:** Record whether a source is suitable for discovery, parameter estimation, validation, burden envelopes or policy context.
- **M-10:** Provide a documented access route rather than merely naming a source.
- **M-11:** Preserve source provenance and transformations through stable identifiers and manifests.

### Architecture and governance

- **M-12:** Use a public-data-first architecture and default to federated analysis for sensitive data.
- **M-13:** Do not commit participant-level, row-level, small-cell or controlled data to Git.
- **M-14:** Allow a custodian to execute common code locally and return approved aggregate outputs.
- **M-15:** Separate public code and metadata from credentials, controlled inputs and restricted outputs.
- **M-16:** Provide patient/community governance over priorities, acceptable use and interpretation.
- **M-17:** Publish conflicts, methods decisions, corrections and release versions.

### Reproducibility and quality

- **M-18:** Validate metadata and analytic inputs against machine-readable schemas.
- **M-19:** Run core validation and tests without network access.
- **M-20:** Record source release, retrieval date, checksum where lawful, transformation version and code commit for each reproducible output.
- **M-21:** Define quality and transportability judgements for each parameter.
- **M-22:** Prevent publication when required provenance, disclosure or uncertainty fields are absent.
- **M-23:** Provide accessible text alongside diagrams and visualisations.

### Initial outputs

- **M-24:** Publish vision, mission, purpose, strategy, architecture and protocol as versioned Markdown.
- **M-25:** Publish the public-source catalogue alpha.
- **M-26:** Publish a gap map showing what public data can and cannot answer.
- **M-27:** Specify at least one rare-within-common demonstrator without overstating available data access.

## Should have

- **S-01:** Crosswalk ORPHAcodes/ORDO with ICD-10/11, MONDO, OMIM, HPO and other selected coding systems.
- **S-02:** Provide a burden-purpose disease hierarchy or linearisation with mutually exclusive aggregation nodes.
- **S-03:** Implement public-source acquisition adapters with cached, versioned raw manifests.
- **S-04:** Produce country-, age- and sex-specific expected affected-population estimates from public denominators and epidemiology.
- **S-05:** Implement one monogenic-diabetes rare-within-common demonstrator.
- **S-06:** Provide an economic-analysis module with declared perspective, currency, price year and discounting.
- **S-07:** Grade evidence quality, bias and cross-country transportability.
- **S-08:** Provide node execution and disclosure-control templates for controlled analyses.
- **S-09:** Archive releases with persistent identifiers through a repository such as Zenodo or OSF.
- **S-10:** Support independent reproduction of published aggregate outputs from released inputs and code.
- **S-11:** Establish at least one LMIC-led or underserved-population node before claims of global representativeness.

## Could have

- **C-01:** Interactive atlas and API over reviewed aggregate outputs.
- **C-02:** Automated ontology-diff alerts and source-release monitoring.
- **C-03:** A synthetic-data package for training and federated pipeline testing.
- **C-04:** Multilingual interface and locally translated policy briefs.
- **C-05:** Scenario modelling for improved diagnosis, treatment or service pathways.
- **C-06:** A reusable OMOP/GA4GH-aligned node runner.
- **C-07:** Automated evidence extraction with mandatory human verification.
- **C-08:** Distributional cost-effectiveness and equity-weighted burden modules.
- **C-09:** Benchmarking against national rare-disease plans and WHO action-plan indicators.

## Won't have in the initial increment

- **W-01:** A central international repository of identifiable or participant-level records.
- **W-02:** Unrestricted redistribution of data whose licence or custodian conditions prohibit it.
- **W-03:** A definitive estimate for every rare disease and every country in the first release.
- **W-04:** Real-time clinical surveillance or individual clinical decision support.
- **W-05:** Automated reclassification of genetic variants for clinical use.
- **W-06:** Causal claims about treatment effects based solely on ecological or cross-sectional burden data.
- **W-07:** Partner, custodian or institutional endorsement inferred from use of public data.
- **W-08:** Country league tables that ignore uncertainty, ascertainment and data quality.

## Non-functional requirements

| Area | Requirement |
|---|---|
| Privacy | No sensitive data in public Git; least-privilege controlled analysis; custodian disclosure rules prevail |
| Security | No secrets in source; dependency and secret scanning before public hosting |
| Reproducibility | Pinned source releases, schemas, deterministic transformations and executable tests |
| Portability | Open formats and no mandatory proprietary execution platform |
| Auditability | Git history, manifests, decision records and correction notices |
| Accessibility | Plain-language summaries and screen-reader-friendly alternatives to diagrams |
| Performance | Public MVP should run on an ordinary research workstation for selected demonstrators |
| Maintainability | Modular adapters, documented contracts and backward-compatible metadata migrations |
| Sustainability | Low central infrastructure burden; computation moves to data where practical |

## Release acceptance criteria

A pre-v1 release may be labelled ready only when:

1. all Must requirements assigned to that release have evidence of completion;
2. the source register and programme roadmap validate and contain no secrets or controlled records;
3. a clean Git clone and source archive reproduce the documented checks;
4. every published estimate displays provenance, uncertainty and evidence status;
5. assigned scientific, data-governance, patient/community, engineering, security and release gates are documented;
6. limitations clearly distinguish feasibility estimates from authoritative national burden estimates;
7. incomplete downstream tracks are not represented as delivered capabilities.

Stable v1.0 additionally requires every blocking criterion in `docs/v1-acceptance-criteria.md` and a formal multi-lane release decision.
