# System and data architecture

**Status:** Conceptual architecture v0.2; implementation staged through the v1 roadmap

## Architectural summary

RareBurden Commons separates public evidence, controlled analysis and released outputs. Public sources flow through versioned adapters into a provenance-rich evidence core. Controlled data never enter the public platform by default: a node runner executes approved analyses within the custodian environment and exports only disclosure-controlled parameters. The modelling layer combines these parameters with population and burden envelopes while preserving uncertainty and evidence status.

```mermaid
flowchart LR
    subgraph S[Source systems]
        O[Open data and APIs]
        R[Public dashboards and registered downloads]
        C[Controlled cohorts and linked data]
        N[New patient and family collections]
    end

    subgraph A[Access and acquisition]
        OA[Versioned public-source adapters]
        SR[Source and licence register]
        NR[Secure or federated node runner]
        DC[Disclosure control]
    end

    subgraph E[Evidence core]
        ONT[Ontology and coding crosswalk]
        PROV[Provenance and lineage]
        PAR[Parameter and evidence ledger]
        QUAL[Quality, bias and transportability grades]
    end

    subgraph M[Analytic layer]
        ENV[Population and burden envelopes]
        ATTR[Rare-within-common attribution]
        BUR[Health burden models]
        ECON[Economic and social burden models]
        UNC[Uncertainty and sensitivity analysis]
    end

    subgraph P[Public products]
        CAT[Data and gap catalogue]
        ATLAS[Burden atlas and country profiles]
        POLICY[Policy and investment products]
        API[Reviewed aggregate data and API]
    end

    subgraph G[Cross-cutting governance]
        PAT[Patient and community governance]
        SCI[Scientific methods review]
        ETH[Data governance and ethics]
        REL[Release, correction and conflict controls]
    end

    O --> OA
    R --> OA
    OA --> SR
    OA --> PROV
    C --> NR
    N --> NR
    NR --> DC
    DC --> PAR
    SR --> PAR
    ONT --> PAR
    PROV --> PAR
    QUAL --> PAR
    PAR --> ENV
    PAR --> ATTR
    ENV --> BUR
    ATTR --> BUR
    ATTR --> ECON
    BUR --> UNC
    ECON --> UNC
    UNC --> CAT
    UNC --> ATLAS
    UNC --> POLICY
    UNC --> API
    PAT -. oversight .-> E
    PAT -. oversight .-> P
    SCI -. review .-> M
    ETH -. approval .-> A
    REL -. release gate .-> P
```

## Trust boundaries

1. **Public zone:** code, schemas, metadata, public aggregate inputs and approved outputs.
2. **Local working zone:** downloaded data permitted for local analysis but not necessarily redistribution.
3. **Controlled node zone:** participant-level data and sensitive outputs subject to custodian controls.
4. **Release boundary:** only reviewed, licensed and disclosure-safe aggregate artefacts cross into the public zone.

## Federated analysis sequence

The core team defines an estimand and portable package. A local node reviews it, executes it under local approvals, applies disclosure control and returns only approved metadata and summary parameters. The commons validates structure and combines the result with other evidence; it does not receive the underlying records.

```mermaid
sequenceDiagram
    participant Core as RareBurden core
    participant Gov as Node governance
    participant Env as Secure data environment
    participant QC as Local disclosure review
    participant Pub as Public evidence core

    Core->>Gov: Submit protocol, code, variables and output contract
    Gov-->>Core: Approve, amend or decline
    Gov->>Env: Authorise versioned analysis package
    Env->>Env: Run local validation and analysis
    Env->>QC: Submit aggregate outputs and logs
    QC-->>Env: Suppress, revise or approve
    QC-->>Core: Export approved parameters and metadata
    Core->>Pub: Validate schema, provenance and version
    Pub->>Pub: Combine evidence and propagate uncertainty
    Pub-->>Gov: Return draft interpretation for review
```

## Core metadata model

The metadata model keeps sources, releases, variables, disease definitions, parameters, analyses and outputs distinct. This permits a parameter to be re-used or invalidated when a source or ontology version changes.

```mermaid
erDiagram
    SOURCE ||--o{ SOURCE_RELEASE : publishes
    SOURCE_RELEASE ||--o{ VARIABLE : contains
    SOURCE_RELEASE ||--o{ PARAMETER : supports
    DISEASE_DEFINITION ||--o{ PARAMETER : defines
    GEOGRAPHY ||--o{ PARAMETER : locates
    PARAMETER }o--o{ ANALYSIS : enters
    ANALYSIS ||--o{ OUTPUT : produces
    ANALYSIS ||--o{ DECISION_RECORD : governed_by
    OUTPUT ||--o{ RELEASE : included_in

    SOURCE {
      string source_id PK
      string custodian
      string access_class
      string licence
    }
    SOURCE_RELEASE {
      string release_id PK
      string source_id FK
      date released_on
      date retrieved_on
      string checksum
    }
    DISEASE_DEFINITION {
      string definition_id PK
      string ontology
      string ontology_version
      string inclusion_rule
    }
    PARAMETER {
      string parameter_id PK
      string estimand
      string evidence_status
      number value
      number lower
      number upper
    }
    ANALYSIS {
      string analysis_id PK
      string code_commit
      string protocol_version
      string status
    }
    OUTPUT {
      string output_id PK
      string disclosure_status
      string provenance_uri
    }
```

## Component responsibilities

### Source register

Discovery and access metadata only; it must not contain secrets. Each source records suitability, access route, terms, release cadence and known limitations.

### Ontology and coding service

Maintains versioned disease definitions, crosswalks and burden-purpose aggregation. It records one-to-many mappings and uncertainty rather than forcing false equivalence.

### Parameter ledger

Stores estimands and evidence, not merely values. Every parameter carries population, period, disease definition, source release, evidence status, uncertainty, bias and transportability metadata.

### Modelling engine

Combines parameters according to a registered analysis specification. Modules remain separate for expected affected population, rare-within-common attribution, health burden and economic/social burden.

### Node runner

A portable package containing code, environment specification, variable contract, tests and disclosure-output template. It should be executable without outbound internet where secure environments require it.

### Release service

Builds versioned aggregate releases, documentation and machine-readable manifests after scientific, governance and disclosure approval.

## Deployment evolution

### Foundation

Git repository, static documentation, YAML/JSON metadata, local validation and manually downloaded public sources.

### Public-data MVP

Automated adapters, Parquet/DuckDB evidence store, reproducible Quarto reports and archived releases.

### Federated network

Containerised or environment-portable node packages, signed manifests, schema-compatible outputs and a reviewed public aggregate API.

## Security and privacy controls

- secrets scanning and no credentials in Git;
- source-specific licence and permitted-use checks;
- controlled data analysed only in approved environments;
- local disclosure thresholds and inferential disclosure review;
- minimum necessary variables and outputs;
- immutable release manifests and audit logs;
- no public model output that permits reconstruction of prohibited small cells;
- incident, correction and withdrawal procedures before controlled nodes launch.


## V1 delivery controls

The component architecture is implemented through the release and track gates in `docs/roadmap-v1.md`. The separate delivery diagrams in `docs/design/v1-delivery-architecture.md` show track lifecycle, assurance and release evidence. A component is not treated as production-ready merely because it appears in this conceptual diagram.
