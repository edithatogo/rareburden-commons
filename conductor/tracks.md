# Track register

**Stable target:** v1.0.0  
**Normative machine-readable plan:** [`roadmap.yml`](roadmap.yml)  
**Current release:** v0.3.0 — Evidence acquisition foundation

Track identifiers 003–005 retain the subjects proposed in v0.1. Execution order is governed by dependencies and target releases, not numeric order.

| ID | Track | Status | Priority | Target | Owner role | Depends on |
|---|---|---|---|---|---|---|
| 001 | Foundation and public-data protocol | Complete | Must | v0.1.0 | Founding team | — |
| 006 | v1 delivery system and foundation hardening | Complete | Must | v0.2.0 | Product and Engineering Leads | 001 |
| 002 | Public-source acquisition and provenance adapters | In review | Must | v0.3.0 | Data Engineering Lead | 001, 006 |
| 007 | Landscape, adjacency, novelty and partnership map | In review | Must | v0.3.0 | Programme and Evidence Synthesis Leads | 001, 006 |
| 018 | Scholarly provenance, protocol transparency and reproducibility | Complete | Must | v0.3.0 | Methods Assurance and Research Software Leads | 001, 006 |
| 008 | Semantic backbone and burden-purpose hierarchy | Blocked | Must | v0.4.0 | Semantic Methods Lead | 002, 007 |
| 009 | Evidence and parameter ledger | Blocked | Must | v0.4.0 | Epidemiology and Data Architecture Leads | 002, 008 |
| 010 | Public burden engine and uncertainty framework | Blocked | Must | v0.5.0 | Statistical and Scientific Software Leads | 009 |
| 003 | Monogenic diabetes rare-within-common demonstrator | Blocked | Must | v0.5.0 | Clinical and Epidemiology Leads | 008, 009, 010 |
| 004 | Federated country-node execution package | Blocked | Must | v0.6.0 | Node Architecture and Data Governance Leads | 006, 009, 010 |
| 011 | Bronchiectasis rare-aetiology demonstrator | Blocked | Must | v0.6.0 | Respiratory Clinical and Epidemiology Leads | 008, 009, 010 |
| 005 | Patient, family, economic and social burden module | Blocked | Must | v0.7.0 | Health Economics and Patient-Reported Outcomes Leads | 009, 010 |
| 012 | Collective paediatric rare-disease burden demonstrator | Blocked | Must | v0.7.0 | Paediatric, Administrative Data and Health Economics Leads | 004, 005, 008, 009, 010 |
| 013 | Quality, validation, gap mapping and equity assurance | Planned | Must | v0.8.0 | Methods Assurance and Equity Leads | 003, 005, 007, 010, 011, 012 |
| 014 | Atlas, API and reproducible release engineering | Planned | Must | v0.8.0 | Product, Data and Release Engineering Leads | 002, 009, 010, 013 |
| 015 | Operational governance, partnerships and policy translation | Planned | Must | v0.9.0 | Programme Director and Patient Community Co-chair | 006, 007, 013 |
| 016 | Security, reliability, performance and operations | Planned | Must | v0.9.0 | Security and Site Reliability Leads | 004, 014 |
| 017 | Documentation, adoption, sustainability and stable v1 release | Planned | Must | v1.0.0 | Product, Documentation and Programme Leads | 013, 014, 015, 016 |

## Status definitions

- **Planned:** specification and plan exist, but dependencies or entry conditions are not yet satisfied.
- **Ready:** dependencies are satisfied and an accountable role can start the track.
- **Active:** implementation is in progress with plan evidence committed incrementally.
- **Blocked:** a named dependency, approval, risk or review finding prevents work.
- **In review:** implementation tasks are complete and formal review is underway.
- **Complete:** acceptance criteria pass, all required tasks are checked and `review.md` records the disposition.
- **Archived:** superseded or stopped with rationale and history retained.

## Parallel work now permitted

Tracks 002, 007 and 018 form the v0.3 release. Track 018 is internally complete; Tracks 002 and 007 remain in review pending external evidence. No downstream track should be marked Active until the validator confirms its dependencies are complete and its owner role is assigned.
