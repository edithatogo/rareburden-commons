# Track 012 specification — Collective paediatric rare-disease burden demonstrator

## Objective

Specify and validate a federated administrative-data analysis of collective paediatric rare-disease mortality, hospital use, cost and diagnostic pathways, initially oriented to Australian and New Zealand settings and designed for wider replication.

## Required outputs

- demonstrator protocol RBC-P004;
- paediatric rare-disease coding and phenotype definition package;
- person-level deduplication and multimorbidity rules for local execution;
- hospitalisation, mortality, utilisation and cost estimands;
- Australian and New Zealand data-access and node specifications;
- synthetic linked-data fixture and federated analysis package;
- disclosure-control and small-number plan;
- transferability specification for at least one differently governed setting;
- public aggregate reporting template and economic linkage.

## Acceptance criteria

1. People rather than diagnosis rows are the primary collective-burden unit where local data permit.
2. Multiple rare diagnoses and common comorbidities are handled without double counting people.
3. Age, period, geography and observation windows are explicit.
4. Costs and utilisation use consistent denominators and perspectives.
5. Synthetic end-to-end node execution passes before real-data application.
6. Local ethics, custodian and disclosure requirements can override generic defaults.
7. Public outputs contain no unsafe small cells or inferentially disclosive combinations.
8. Replication requirements for a non-Australasian node are documented.

## Non-goals

- assuming administrative coding captures all rare disease;
- transferring Australian or New Zealand estimates globally without validation;
- centralising linked records;
- using burden estimates to restrict access to care.

## v1 contribution

This track exercises person-level deduplication, controlled data, economic linkage and paediatric policy translation.

## Non-binding protocol draft — RBC-P004 v0.1.0 (2026-07-27)

Preparatory only; this does not activate the track, authorise person-level access or freeze a paediatric contract. Define aggregate and, only where approved, person-level estimands for incidence/prevalence, admissions, mortality, costs and service use by jurisdiction and observation window. Document Australian/New Zealand custodian pathways, linkage authority, Indigenous/data-governance, retention and withdrawal conditions. Use synthetic person/diagnosis/admission/death/cost tables with deduplication, multimorbidity, small-cell and suppression cases; export approved aggregates only. Paediatric/clinical, economics, privacy/governance, security, patient/family and engineering review are required.
