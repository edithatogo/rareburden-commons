# ADR-0001: Public-data-first, federated architecture

- **Status:** Accepted for foundation
- **Date:** 2026-07-18
- **Decision owners:** Founding project; to be ratified by future scientific and patient/community governance

## Context

The required evidence is distributed across open international datasets, disease knowledge bases, genomic cohorts, registries, administrative linkage systems and patient-reported collections. Most detailed health records cannot lawfully or practically be transferred into a new international repository. Asking for unrestricted source microdata would create avoidable delay, privacy risk and institutional resistance.

## Decision

RareBurden Commons will:

1. build the first useful release from public and routinely accessible aggregate data;
2. maintain a source and access catalogue before seeking data;
3. use controlled data through established secure research pathways;
4. prefer custodian-side execution of portable code where feasible;
5. accept only disclosure-reviewed aggregate parameters from federated nodes;
6. prohibit participant-level or controlled records in the public repository;
7. combine estimates through a provenance-rich parameter ledger rather than identity linkage.

## Consequences

### Positive

- lower privacy and cross-border risk;
- faster public-data proof of value;
- clearer, smaller asks of custodians;
- greater portability across countries and institutions;
- preserves local governance and supports sovereign data arrangements;
- makes source heterogeneity and uncertainty explicit.

### Negative and trade-offs

- individual-level cross-source linkage is generally unavailable;
- harmonisation and transportability modelling become central and difficult;
- secure environments may require multiple implementations or packaging formats;
- disclosure controls can limit subgroup detail;
- federated estimates may be delayed by local capacity and approvals;
- some causal and multimorbidity questions remain unanswerable without deeper linkage.

## Alternatives rejected

### Central international data lake

Rejected as the default because it is unnecessary for the first estimands, unlikely to obtain comprehensive participation and creates disproportionate governance and security burden.

### Literature review only

Rejected because it would not create reusable access metadata, executable methods or a path to controlled country validation.

### Disease-registry federation only

Rejected because registry ascertainment is selective and cannot alone supply population denominators, common-disease envelopes or full economic burden.

## Revisit triggers

Reconsider this decision if a lawful, patient-supported international infrastructure offers materially better linkage with proportionate risk, or if a defined estimand cannot be answered through aggregate/federated evidence and has sufficient public value to justify a different architecture.
