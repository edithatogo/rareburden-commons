# V1 delivery architecture

## Release flow

The delivery system moves from programme definition to a stable supported release. Gates can narrow or stop a release; they are not ceremonial approvals.

```mermaid
flowchart LR
    F[v0.1 Foundation] --> C[v0.2 Programme control]
    C --> A[v0.3 Acquisition and novelty]
    A --> S[v0.4 Semantic evidence core]
    S --> B[v0.5 Burden engine alpha]
    B --> N[v0.6 Federated methods alpha]
    N --> E[v0.7 Economic and paediatric beta]
    E --> P[v0.8 Validated atlas beta]
    P --> R[v0.9 Release candidate]
    R --> V[v1.0 Stable]

    G1{Scientific gate} -. blocks .-> B
    G2{Data and privacy gate} -. blocks .-> N
    G3{Patient and equity gate} -. blocks .-> P
    G4{Security and operations gate} -. blocks .-> R
    G5{Independent reproduction gate} -. blocks .-> V
```

The scientific product remains a versioned static release even when a hosted API or atlas is available. This preserves an immutable source of truth.

## Track lifecycle

```mermaid
stateDiagram-v2
    [*] --> Planned
    Planned --> Ready: dependencies and owner satisfied
    Ready --> Active: implementation begins
    Active --> Blocked: approval, risk or dependency failure
    Blocked --> Active: blocking issue resolved
    Active --> InReview: plan tasks complete
    InReview --> Active: review fixes required
    InReview --> Complete: acceptance and gates pass
    Planned --> Archived: stopped or superseded
    Blocked --> Archived: redesign or stop decision
    Complete --> [*]
```

A track cannot be Complete without a review record. A release cannot count incomplete tracks as evidence.

## Assurance pipeline

```mermaid
flowchart TD
    Q[Question and estimand] --> D[Disease definition and hierarchy]
    D --> SR[Source and release manifests]
    SR --> L[Evidence and parameter ledger]
    L --> M[Model and uncertainty specification]
    M --> T[Automated and scientific tests]
    T --> X[Disclosure and acceptable-use review]
    X --> I[Independent reproduction]
    I --> RP[Immutable release package]

    SCI[Scientific review] -.-> D
    SCI -.-> M
    GOV[Data governance] -.-> SR
    GOV -.-> X
    PAT[Patient/community governance] -.-> Q
    PAT -.-> X
    ENG[Engineering and security] -.-> T
    ENG -.-> RP
```

Each released estimate must trace backwards through this chain. A missing link is a release-blocking provenance defect.

## Release evidence package

```mermaid
flowchart LR
    CODE[Code and Git commit] --> MAN[Release manifest]
    DATA[Source and acquisition manifests] --> MAN
    SEM[Semantic release] --> MAN
    LED[Parameter ledger] --> MAN
    PROT[Protocols and analysis specification] --> MAN
    TEST[Test, validation and review reports] --> MAN
    MAN --> PKG[Signed/checksummed release package]
    PKG --> ARC[Persistent archive]
    PKG --> ATLAS[Static atlas and data package]
    PKG --> API[Versioned API representation]
```

The atlas and API are generated representations of the reviewed release package. They do not read directly from mutable working data.
