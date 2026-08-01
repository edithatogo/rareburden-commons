# Subagent panel report — stable v1 candidate

**Date:** 2026-08-01  
**Status:** preparatory review; not human approval or publication authority

Three independent read-only panel roles reviewed the current evidence packet:
scientific methods, governance/patient-community/custodian, and
security/release/operations.

## Dispositions

| Panel | Recommendation |
|---|---|
| Scientific methods | `bounded` for public/synthetic preparation; `revise` for stable v1 or atlas/API beta |
| Governance/patient/community/custodian | `bounded` for public/synthetic preparation; `stop` for controlled activation, patient-facing/policy/global claims or stable-v1 authorization |
| Security/release/operations | `bounded`/`revise`, not `pass` |

## Accepted repository evidence

- Fail-closed schemas with explicit uncertainty, missingness and transportability.
- Locked dependencies, SBOM/checksum controls and release-attestation tooling.
- Synthetic reproducibility and installed-package validation.
- Explicit bounded public/synthetic scope in ADR-0007.

## Required external receipts

- Independent human reproduction and usability report.
- Scientific triangulation, calibration, sensitivity and model-criticism reports.
- Empirical equity, LMIC and Indigenous governance assessment.
- Named accountable scientific, governance, security and operational owners.
- Security/vulnerability tabletop and backup/restore/rollback transcripts.
- Written custodian authorization for controlled-node or pilot work.
- Final release-authority decision tied to the exact candidate digest.

Subagent reports cannot provide consent, ethics approval, custodian authority,
institutional commitment or publication authorization. Until those receipts
arrive, controlled data, hosted API activation, global/patient-facing/policy
claims and stable-v1 publication remain excluded.
