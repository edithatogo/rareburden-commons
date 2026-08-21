# Track register

**Stable target:** v1.0.0  
**Normative machine-readable plan:** [`roadmap.yml`](roadmap.yml)  
**Current release:** v0.3.0 — Evidence acquisition foundation

Track identifiers 003–005 retain the subjects proposed in v0.1. Execution order is governed by dependencies and target releases, not numeric order.

| ID | Track | Status | Priority | Target | Owner role | Depends on |
|---|---|---|---|---|---|---|
| 001 | Foundation and public-data protocol | Archived | Must | v0.1.0 | Founding team | — |
| 006 | v1 delivery system and foundation hardening | Complete | Must | v0.2.0 | Product and Engineering Leads | 001 |
| 002 | Public-source acquisition and provenance adapters | Archived | Must | v0.3.0 | Data Engineering Lead | 001, 006 |
| 007 | Landscape, adjacency, novelty and partnership map | Archived | Must | v0.3.0 | Programme and Evidence Synthesis Leads | 001, 006 |
| 018 | Scholarly provenance, protocol transparency and reproducibility | Archived | Must | v0.3.0 | Methods Assurance and Research Software Leads | 001, 006 |
| 008 | Semantic backbone and burden-purpose hierarchy | Blocked | Must | v0.4.0 | Repository owner (sole accountable human) | 002, 007 |
| 009 | Evidence and parameter ledger | Blocked | Must | v0.4.0 | Repository owner (sole accountable human) | 002, 008 |
| 010 | Public burden engine and uncertainty framework | Blocked | Must | v0.5.0 | Repository owner (sole accountable human) | 009 |
| 003 | Monogenic diabetes rare-within-common demonstrator | Blocked | Must | v0.5.0 | Repository owner (sole accountable human) | 008, 009, 010 |
| 004 | Federated country-node execution package | Blocked | Must | v0.6.0 | Repository owner (sole accountable human) | 006, 009, 010 |
| 011 | Bronchiectasis rare-aetiology demonstrator | Blocked | Must | v0.6.0 | Repository owner (sole accountable human) | 008, 009, 010 |
| 005 | Patient, family, economic and social burden module | Blocked | Must | v0.7.0 | Repository owner (sole accountable human) | 009, 010 |
| 012 | Collective paediatric rare-disease burden demonstrator | Blocked | Must | v0.7.0 | Repository owner (sole accountable human) | 004, 005, 008, 009, 010 |
| 013 | Quality, validation, gap mapping and equity assurance | Blocked | Must | v0.8.0 | Repository owner (sole accountable human) | 003, 005, 007, 010, 011, 012 |
| 014 | Atlas, API and reproducible release engineering | Blocked | Must | v0.8.0 | Repository owner (sole accountable human) | 002, 009, 010, 013 |
| 015 | Operational governance, partnerships and policy translation | Blocked | Must | v0.9.0 | Repository owner (sole accountable human) | 006, 007, 013 |
| 016 | Security, reliability, performance and operations | Planned | Must | v0.9.0 | Repository owner (sole accountable human) | 004, 014 |
| 017 | Documentation, adoption, sustainability and stable v1 release | Planned | Must | v1.0.0 | Repository owner (sole accountable human) | 013, 014, 015, 016 |

## Status definitions

- **Planned:** specification and plan exist, but dependencies or entry conditions are not yet satisfied.
- **Ready:** dependencies are satisfied and an accountable role can start the track.
- **Active:** implementation is in progress with plan evidence committed incrementally.
- **Blocked:** a named dependency, approval, risk or review finding prevents work.
- **In review:** implementation tasks are complete and formal review is underway.
- **Complete:** acceptance criteria pass, all required tasks are checked and `review.md` records the disposition.
- **Archived:** superseded or stopped with rationale and history retained.

## Parallel work now permitted

Tracks 002, 007 and 018 form the v0.3 release. Tracks 007 and 018 are archived
after bounded internal completion. Track 002 is archived after completion of its bounded
acquisition/provenance substrate and exact owner-dispositioned source roles;
publication and optional source expansion remain separate. Track 007 external
registry submission is optional and its broader landscape ambitions require a
separately versioned future scope. No downstream track should be marked Active
until the validator confirms its dependencies are complete and its owner role
is assigned.

## Single-developer review mode

Review evidence for every track is produced by a role-separated agent panel
under `docs/decisions/ADR-0009-agent-panel-owner-governance.md`. Track plans
must not imply another maintainer, human reviewer or independent review. Panels
advise and the repository owner records the accountable disposition.

The repository owner (`edithatogo`) is the sole accountable human, owner,
maintainer, scientist, developer, operator, security decision-maker and release
decision-maker. Owner-operated implementation, scientific
review, validation, support preparation, reproduction and bounded release
decisions are permitted and must be labelled as owner-operated repository
evidence, not independent approval or external validation. The community/harm
lane is an owner-executed simulated-community challenge and never represents
actual participation, consultation, consent or endorsement.
No backup owner, co-maintainer, agent, bot or external evidence provider holds
repository accountability. Recovery material and procedures do not confer
authority. Owner-operated operator/security evidence and owner release
decisions must be labelled accurately and bound to the exact candidate.

The dependency-ordered panel workflow for methods, community/harm,
rights/data-use, operator/security and release advice is documented
in [`panel-gate-plan.md`](panel-gate-plan.md). Panels prepare and challenge
packets; the repository owner adjudicates them. Publisher rights and future
controlled-data custodian policies remain factual constraints.

The current candidate-bound ledger is maintained in
[`docs/remaining-gates-current-state-2026-08-03.md`](../docs/remaining-gates-current-state-2026-08-03.md).

The dependency-ordered downstream preparation boundary for Tracks 008–017 is
maintained in
[`docs/downstream-bounded-preparation-plan-2026-08-03.yml`](../docs/downstream-bounded-preparation-plan-2026-08-03.yml).
