# Requirements traceability

**Status:** v0.3.0rc2 autonomous-development handoff candidate
**Evidence rule:** a requirement is complete only when the cited artefact exists,
applicable automated verification passes, and the role-separated agent-panel
challenge plus attributable owner disposition are documented. This repository
does not claim independent human approval; publisher, custodian and other
third-party facts remain separately evidence-bound. Synthetic reference
evidence is not empirical validation.

## Status vocabulary

| State | Meaning |
|---|---|
| Implemented — reference | Executable and verified against synthetic/public fixtures; external or empirical validation may still be required. |
| Partial | A meaningful substrate exists, but one or more blocking acceptance criteria remain open. |
| External gate | The remaining evidence depends on an approval, licence decision, independent review, controlled environment or real-world node. |
| Planned | No implementation sufficient for the requirement yet exists. |

## Must requirements

| Requirement | Primary track(s) | Current evidence | Current state and remaining gate |
|---|---:|---|---|
| M-01 Versioned rare-disease inclusion framework | 008 | `schemas/disease-hierarchy.schema.json`; `src/rareburden/semantics.py`; synthetic hierarchy fixtures and tests | **Partial:** executable versioned hierarchy preview exists; governed real ORPHA/ICD/MONDO/OMIM inclusion releases and clinical review remain open. |
| M-02 Record ontology and coding releases | 008 | `schemas/ontology-mapping.schema.json`; semantic fingerprints and mapping tests | **Partial:** contracts and synthetic mappings exist; real release descriptors, mapping review state and semantic-diff governance remain open. |
| M-03 Define estimand before analysis | 009, 010 | `schemas/analysis-specification.schema.json`; reference analysis specification | **Implemented — reference:** the reference workflow validates an explicit estimand; empirical demonstrators still require prospectively frozen specifications. |
| M-04 Distinguish evidence status | 009 | `schemas/parameter-ledger.schema.json`; `src/rareburden/ledger.py`; evidence-status tests | **Implemented — reference:** observed, derived, modelled, transferred and assumed states are machine validated. |
| M-05 Explicit overlap and double-counting rules | 008, 010, 011, 012 | `src/rareburden/semantics.py`; hierarchy/aggregation negative tests; burden guards | **Implemented — reference:** non-exclusive summation is blocked without an overlap model; real multi-diagnosis validation remains open. |
| M-06 Propagate uncertainty | 010 | `src/rareburden/stochastic.py`; `burden.py`; `uncertainty.py`; deterministic and Monte Carlo tests | **Implemented — reference:** fixed and distributional parameters, intervals and seeded simulation are executable; empirical calibration/correlation review remains open. |
| M-07 Machine-readable source register | 001, 002 | `catalog/data_sources.yml`; source/release/acquisition schemas; catalogue validator | **Implemented — reference:** 14 seed sources validate; live access, current terms, release discovery and custodian verification remain open per source. |
| M-08 Access-class taxonomy | 001, 002 | catalogue schema and validation | **Implemented:** open/API, public/registration, controlled research, federated partner and new collection are distinguished. |
| M-09 Record source analytic suitability | 002, 009 | catalogue purpose/use fields; evidence assessments; quality dispositions | **Partial:** reference contracts exist; every production source/parameter still needs a dated fitness-for-use judgement. |
| M-10 Document access route | 001, 002 | catalogue access instructions; acquisition adapters; manual-artifact registrar | **Partial:** executable lawful acquisition/manual-registration paths exist; live source terms and operational evidence remain open. |
| M-11 Stable provenance and manifests | 002, 009, 014, 018 | source-release, acquisition, normalisation, transformation, workflow, lineage and release manifests; seven-gate verifier | **Implemented — reference:** content-addressed end-to-end lineage is verified for the synthetic release; production sources require the same evidence. |
| M-12 Public-data-first and federated architecture | 001, 004 | ADR, architecture documents, public reference workflow, synthetic node preview | **Partial:** public-data-first execution works; production federated node and custodian deployment remain open. |
| M-13 No sensitive data in Git | 001, 016 | repository-safety checker; contribution/security policy; synthetic-only fixtures | **Implemented for repository controls:** hosted secret scanning and operational security review remain release gates. |
| M-14 Local custodian execution | 004 | node input/output/policy/manifest schemas; packaged synthetic runner; operator guide | **Partial / external gate:** aggregate allowlists, threshold non-weakening, query budgets and deterministic package checks exist; second-operator installation, approved custodian pilot and controlled deployment remain open. |
| M-15 Separate public and restricted zones | 001, 004, 016 | trust-zone architecture; local/export manifest separation; path/security tests | **Partial:** design and synthetic separation exist; production threat model and controlled-environment validation remain open. |
| M-16 Patient/community governance | 015 | governance principles and agent-panel harm/framing challenge | **Bounded repository mode:** no patient/community authority or consent is claimed; owner disposition must remove patient-facing or community-legitimacy claims unless separately evidenced. |
| M-17 Publish conflicts, methods decisions and corrections | 015, 017, 018 | prospective protocol, decision log, release records, contribution/governance policies | **Partial:** machine-readable decision and amendment infrastructure exists; operational conflicts, corrections, appeals and publication governance remain open. |
| M-18 Schema-validate metadata and inputs | 001, 002, 004, 008, 009, 014, 018 | JSON Schemas; schema meta-validator; strict YAML and node fixture checks | **Implemented — reference:** the current schema collection and node contract fixtures validate; migration/backward-compatibility policy remains a v1 task. |
| M-19 Core validation works offline | 001, 004, 016, 018 | offline programme validation; packaged reference repository; synthetic workflow and verifier | **Implemented — reference:** installed wheel can validate and run the reference workflow without network; full locked cross-platform hosted evidence remains open. |
| M-20 Record release, checksum, transform and commit | 002, 009, 014, 018 | activity-level transformation records, workflow graph, release manifest, Git/tree state, hashes | **Implemented — reference:** every reference output closes to source, activity and release evidence. |
| M-21 Quality and transportability judgement | 009, 013 | evidence/transportability/quality-disposition schemas and engine | **Implemented — reference:** intended-use gates and transported-evidence requirements are executable; external methods review remains open. |
| M-22 Block release when mandatory fields are absent | 009, 013, 014, 018 | fail-closed schemas, negative tests and independent verifier | **Implemented — reference:** malformed provenance, incompatible scientific use and incomplete release closure are rejected. |
| M-23 Accessible text for diagrams and visualisations | 014, 017 | prose architecture descriptions and documentation policy | **Partial:** documentation provides textual alternatives; formal accessibility audit of atlas/API outputs remains open. |
| M-24 Publish founding documents | 001 | versioned vision, mission, purpose, strategy, architecture and protocol | **Complete.** |
| M-25 Publish source-catalogue alpha | 001 | validated catalogue | **Complete at alpha level.** |
| M-26 Publish public-data gap map | 013 | `schemas/gap-map.schema.json`; `src/rareburden/gapmap.py`; reference gap map | **Implemented — reference:** machine-readable public-data readiness classification is generated; empirical global review and rendered atlas remain open. |
| M-27 Specify rare-within-common demonstrator | 001, 003 | analysis contracts, semantic preview and fully synthetic rare-aetiology analysis | **Partial:** executable synthetic demonstration exists; prospectively registered monogenic-diabetes protocol and empirical inputs remain open. |

## Should requirements

| Requirement | Track(s) | Current state |
|---|---:|---|
| S-01 Semantic crosswalk | 008 | **Partial:** schema and synthetic mappings exist; governed real mappings remain open. |
| S-02 Burden-purpose hierarchy | 008 | **Partial:** executable hierarchy and aggregation controls exist; production linearisation/review remain open. |
| S-03 Public-source adapters | 002 | **Partial:** secure adapter framework plus Orphadata/UN/WHO/World Bank fixture normalisers exist; live terms/version tests remain open. |
| S-04 Expected affected-population estimates | 010 | **Implemented — reference:** deterministic and stochastic public-denominator calculations exist. |
| S-05 Monogenic-diabetes demonstrator | 003 | **Partial:** synthetic rare-aetiology path exists; empirical protocol, data and validation remain open. |
| S-06 Economic module | 005 | **Planned:** current guards prevent misuse of cost envelopes, but no production economic module exists. |
| S-07 Evidence quality and transportability | 009, 013 | **Implemented — reference:** domain judgements and intended-use disposition are executable. |
| S-08 Node and disclosure templates | 004 | **Partial:** packaged synthetic node, allowlisted aggregate outputs, small-cell suppression, monotonic custodian thresholds, overlap-query budgets, strict manifests, log redaction and a keyless offline-verifiable release profile exist; real tagged-release verification, independent operator, custodian review and controlled pilot remain open. |
| S-09 Persistent release archive | 014, 017, 018 | **Partial / external gate:** CFF, CodeMeta, Zenodo, DataCite-oriented and RO-Crate metadata exist; DOI deposition and independent preservation remain open. |
| S-10 Owner-operated reproduction | 013, 017, 018 | **Repository gate:** exact clean-environment owner-operated reproduction may support bounded evidence; it is never represented as independent or external reproduction. |
| S-11 LMIC-led or underserved node | 015 | **External gate:** required before unqualified global-representativeness claims. |

## Could requirements promoted for mature v1 scope

| Requirement | Track(s) | Current state |
|---|---:|---|
| C-01 Reviewed atlas and API | 014 | Planned for v0.8. |
| C-03 Synthetic node test package | 004 | **Implemented — bounded reference:** four node schemas, aggregate allowlists, suppression, supplied-history query guards, strict manifests and installed-wheel execution are tested; independent operator and controlled validation remain open. |
| C-06 Reusable interoperable node runner | 004, 008 | **Partial:** the installed wheel exercises the explicitly synthetic common-analysis, immutable policy/query-ledger and aggregate-export primitives; a deterministic local-wheel bundle is implemented. Production contract approval, complete locked wheel staging, custodian-controlled durable ledger, standards alignment and controlled deployment remain open. |
| C-09 Policy/action-plan indicators | 015 | Planned as a reviewed translation layer. |

Other Could requirements remain post-v1 candidates unless adopted through change control.

## Current handoff evidence

At the handoff marker, the repository has demonstrated offline:

- programme validation across 18 Conductor tracks and 10 gated releases;
- validation of 30 JSON Schemas;
- reference-workflow generation and seven-gate independent verification;
- exact two-process, cross-hash-seed reproduction of the synthetic release;
- deterministic wheel and canonicalised source-distribution construction;
- installed-wheel discovery of its packaged reference repository;
- repository-safety, lockfile, requirements-export, workflow-policy and release-identity checks;
- the available single-process core suite in this environment.

The complete exact locked development harness—including Hypothesis, strict typing, Ruff, hosted security workflows and live vulnerability queries—must be rerun by Codex/hosted CI before any final release decision.

## Traceability maintenance

- Track plans must cite requirement IDs for every material task.
- Tests should use requirement IDs in names or metadata where practical.
- A release candidate must regenerate or independently review this table.
- Deferred Must requirements require an explicit scope-removal decision; they cannot remain silently open.
- A synthetic or internal artefact may support implementation evidence, but cannot satisfy an external-governance, empirical-validation or independent-reproduction gate.
