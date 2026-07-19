# Requirements traceability

**Status:** v0.2.0 planning baseline  
**Rule:** a requirement is complete only when the cited artefact exists and the applicable verification passes.

## Must requirements

| Requirement | Primary implementation track(s) | v1 evidence target | Current state |
|---|---|---|---|
| M-01 Versioned rare-disease inclusion framework | 008 | Disease-definition releases and hierarchy tests | Planned |
| M-02 Record ontology and coding releases | 008 | Mapping schema, release manifest and diff report | Planned |
| M-03 Define estimand before analysis | 009, 010 | Machine-readable analysis specification | Planned |
| M-04 Distinguish evidence status | 009 | Parameter-ledger validation and output audit | Planned |
| M-05 Explicit overlap and double-counting rules | 008, 010, 011, 012 | Hierarchy and multi-diagnosis test suite | Planned |
| M-06 Propagate uncertainty | 010 | Statistical and sensitivity tests | Planned |
| M-07 Machine-readable source register | 001, 002 | Extended source/release schemas and validated catalogue | Partial: source catalogue exists |
| M-08 Access-class taxonomy | 001, 002 | Catalogue validation | Implemented at foundation level |
| M-09 Record source analytic suitability | 002, 009 | Source and parameter contracts | Partial |
| M-10 Document access route | 001, 002 | Tested adapter or manual registration guide | Partial: descriptive routes exist |
| M-11 Stable provenance and manifests | 002, 009, 014 | End-to-end lineage audit | Planned |
| M-12 Public-data-first and federated architecture | 001, 004 | Architecture and node tests | Architecture complete; execution planned |
| M-13 No sensitive data in Git | 001, 016 | Safety/security checks and release audit | Foundation check implemented |
| M-14 Local custodian execution | 004 | Portable node and approved pilot | Planned |
| M-15 Separate public and restricted zones | 001, 004, 016 | Threat model and deployment tests | Designed; implementation planned |
| M-16 Patient/community governance | 015 | Constituted charter and release decisions | Proposed only |
| M-17 Publish conflicts, methods decisions and corrections | 015, 017 | Operational policies and release records | Partial |
| M-18 Schema-validate metadata and inputs | 001, 002, 008, 009, 014 | Schema and contract test suite | Source catalogue only |
| M-19 Core validation works offline | 001, 004, 016 | CI and clean offline verification | Foundation validation works offline |
| M-20 Record release, checksum, transform and commit | 002, 009, 014 | Release manifest and lineage audit | Planned |
| M-21 Quality and transportability judgement | 009, 013 | Evidence assessment records | Planned |
| M-22 Block release when mandatory fields are absent | 009, 013, 014 | Release-gate negative tests | Planned |
| M-23 Accessible text for diagrams and visualisations | 014, 017 | Accessibility audit | Documentation principle exists |
| M-24 Publish founding documents | 001 | Versioned repository documents | Complete |
| M-25 Publish source-catalogue alpha | 001 | Validated catalogue release | Complete |
| M-26 Publish public-data gap map | 013 | Machine-readable and rendered gap map | Planned; explicitly outstanding |
| M-27 Specify rare-within-common demonstrator | 001, 003 | Monogenic-diabetes protocol and analysis package | Specification-level complete; implementation planned |

## Should requirements

| Requirement group | Tracks | v1 disposition |
|---|---|---|
| S-01 to S-02 semantic crosswalk and burden hierarchy | 008 | Blocking for supported demonstrators |
| S-03 public-source adapters | 002 | Blocking |
| S-04 expected affected-population estimates | 010 | Blocking |
| S-05 monogenic-diabetes demonstrator | 003 | Blocking |
| S-06 economic module | 005 | Blocking for published economic outputs |
| S-07 evidence quality and transportability | 009, 013 | Blocking |
| S-08 node and disclosure templates | 004 | Blocking |
| S-09 persistent release archive | 014, 017 | Blocking |
| S-10 independent reproduction | 013, 017 | Blocking |
| S-11 LMIC-led or underserved node | 015 | Blocking for unqualified global claims |

## Could requirements promoted for mature v1 scope

The following former Could requirements become part of the stable v1 target because they materially improve maturity:

| Requirement | Track | v1 status |
|---|---|---|
| C-01 reviewed atlas and API | 014 | Included |
| C-03 synthetic node test package | 004 | Included |
| C-06 reusable interoperable node runner | 004, 008 | Included for the supported node contract |
| C-09 policy and action-plan indicators | 015 | Included as a documented translation layer |

Other Could requirements remain post-v1 candidates unless adopted through change control.

## Traceability maintenance

- Track plans must cite requirement IDs for each material task.
- Tests should use requirement IDs in names or metadata where practical.
- A release candidate must regenerate or review this table.
- Deferred Must requirements require an explicit scope-removal decision; they cannot remain silently open.
