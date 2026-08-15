# Public-source data-use and backup-owner disposition

**Decision date:** 2026-08-15  
**Decision-maker:** repository owner (`edithatogo`)  
**Governance:** ADR-0009

## Public-source scope

The former Track 002 `custodian_data_governance` gate is separated into:

1. immutable publisher-licence and third-party-rights facts; and
2. an accountable owner data-use disposition covering repository-controlled
   scope, retention, attribution, withdrawal, transformation and activation.

The active public-source candidates are:

| Source | Rights evidence | Owner disposition |
|---|---|---|
| Orphadata Science July 2026 epidemiology and alignment files | Exact product pages identify the files and CC BY 4.0 | Allow bounded descriptive metadata and identifier alignment with attribution/change notice; no denominator or burden inference |
| UN WPP 2024 compact workbook | Exact workbook embeds CC BY 3.0 IGO | Allow named-geography/year medium-variant denominators with attribution; exclude third-party aggregate-classification fields |
| WHO GHE 2021 country DALY workbook | WHO terms observed, but no file-level licence or field-level third-party register | Candidate/private-metadata posture only; no redistribution or activated derived output until field rights are resolved |
| World Bank SP.POP.TOTL bounded API query | Exact response hash and observed CC BY 4.0 series terms | Probe/cross-check only; never silently substitute for WPP |

Orphadata and WPP do not require a separate public-data custodian review after
their exact rights evidence and owner disposition are recorded. WHO unresolved
third-party rights remain fail-closed. Actual custodian authority is reserved
for a future controlled-data deployment and is excluded from the current
synthetic/public candidate.

## Backup-owner attestation

The repository owner reports that a privacy-preserving backup operational owner
has accepted the role. This records acceptance without publishing personal
identity. Completion of the continuity evidence still requires a stable private
role identifier, accepted support/incident/recovery/succession scope,
escalation route, review/expiry date and a hash-bound handoff exercise. Until
then the state is `owner_attested_private_backup_acceptance`, not a completed
handoff exercise.
