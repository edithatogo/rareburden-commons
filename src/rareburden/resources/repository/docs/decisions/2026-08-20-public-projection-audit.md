# Public projection audit — 2026-08-20

**Decision owner:** repository owner
**Operating model:** single developer; role-separated agent-panel challenge and
owner disposition. No independent, human, patient/community, custodian or
external approval is claimed.

## Decision

Publish or retain in the public Hugging Face projection only exact artifacts
whose recorded source terms permit redistribution. The private archive is not
made public as a whole because it contains licensed or unresolved material.
Where an exact public path already exists, record it as publicized/verified and
do not upload a duplicate or delete the private copy during this audit.

## Publicly eligible projection

The following private-archive source families have exact public counterparts in
`edithatogo/rareburden-commons-open-source-snapshots`:

| Source | Public path | Terms boundary |
|---|---|---|
| Orphadata July 2026 alignment and epidemiology | `raw/orphadata/2026-07/` | CC BY 4.0; attribution and change notice |
| UN WPP 2024 workbook | `raw/wpp/2024/` | CC BY 3.0 IGO; attribution, notices and third-party-field exclusions |
| MONDO v2026-08-04 | `raw/mondo/v2026-08-04/` | CC BY 4.0; exact release and attribution |
| ClinVar August 2026 snapshot | `raw/clinvar/2026-08/` | Public download; NCBI and submitter attribution |
| World Bank bounded probe | `probe/world-bank/2026-08-15/` | Exact observed series terms; probe-only, no WPP substitution |

The repository records these as public projections, not production activation
or scientific fitness decisions.

## Withheld material

HPO, UMLS, SNOMED/MLDS, MedDRA, WHO GHE/ICD, PanelApp restricted details and
other artifacts with incomplete, territorial, third-party or authenticated
terms remain private or metadata/hash-only. Public availability or owner
authority does not create redistribution permission. No private bytes were
deleted.

## Stop conditions

Rights ambiguity, changed terms, hash mismatch, an unverified public object or a
withdrawal request requires quarantine or metadata-only routing and a new
owner disposition.
