# Track 018 review — Scholarly provenance, protocol transparency and reproducibility

**Review date:** 2026-07-19  
**Decision:** Pass for internal v0.3 release-candidate use; external reproduction remains a later gate

## Acceptance review

| Criterion | Result | Evidence |
|---|---|---|
| Prospective and retrospective evidence are separate | Pass | Protocol registration, decision log and transformation-run contracts |
| Exact activity-level provenance exists | Pass | Transformation records and workflow DAG |
| Interoperable provenance projection exists | Pass | W3C PROV-O JSON-LD bundle and verifier |
| End-to-end lineage closes | Pass | Lineage-audit builder, verifier and negative tests |
| Research object is self-contained for synthetic assurance | Pass | RO-Crate/Process Run Crate reference package |
| Reporting transparency is explicit | Pass | GATHER evidence checklist with non-applicability and limitations |
| Reproducibility claims are conservative | Pass | R0–R4 assessment; reference claims R2 only |
| Scholarly metadata does not fabricate identifiers | Pass | CFF, CodeMeta, Zenodo and DataCite-ready validation |
| Tampering and unsafe evidence paths are detected | Pass | Unit and integration tests |

## Scientific and transparency review

- The native activity and workflow records remain normative; standards projections are interoperable views rather than substitutes for exact project contracts.
- Internal protocol freeze is not labelled preregistration.
- Prospective, implementation and post-hoc decisions are distinguishable.
- The reference package is synthetic and cannot substantiate a disease-burden estimate.
- Structural auditability is not represented as independent reproduction, empirical replication, peer review or governance approval.

## Residual risks and assigned tracks

- Independent reproduction by a separate operator: Tracks 013 and 017.
- External empirical replication: demonstrator tracks 003, 011 and 012.
- Persistent repository deposition and DOI issuance: Tracks 014 and 017.
- Patient/community and data-governance review of release framing: Track 015.
- Hosted supply-chain attestations and protected release environments: Track 016.

## Disposition

Approve the scholarly assurance substrate for inclusion in the v0.3 release candidate. Do not mark v0.3 final until Tracks 002 and 007 pass their external and source-specific gates.
