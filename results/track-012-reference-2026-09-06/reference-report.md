# Track 012: Collective Paediatric Rare-Disease Burden Reference Report

**Protocol ID:** `RBC-P004`  
**Receipt ID:** `demo12-28e2a5bcf24ead3966a75783`  
**Created At:** `2026-09-06T00:00:00Z`  
**Status:** Synthetic reference analysis; no empirical validation or clinical authority.

## 1. Executive Summary

This report records the executed synthetic reference analysis for Track 012 (`012-paediatric-burden-demonstrator`) under protocol RBC-P004. The demonstrator models a collective paediatric rare-disease cohort using linked administrative data (person, diagnosis, admission, death, cost tables) with strict person-level deduplication, multimorbidity accounting, and Track 004 offline federated-node execution.

## 2. Conservation Accounting

| Quantity | Count | Description |
|---|---|---|
| Total Person Records | 2 | Raw linked person table rows |
| Deduplicated People | 2 | Conserved distinct children |
| Diagnosis Records | 3 | Rare disease condition rows |
| Admission Records | 3 | Inpatient hospital episodes |
| Cost Records | 1 | Direct medical cost events |

**Conservation Check Passed:** `True`

## 3. Evaluated Scenarios and Sensitivity

| Scenario ID | Disclosure Floor | Cost Mult | Deduplicated People | | Utilisation Rate | Mean Annual Cost | Suppressed |
|---|---|---|---|---|---|---|
| `baseline-primary-linkage` | 2 | 1.0 | **2** | 1.50 | $500.00 | True |
| `strict-disclosure-suppression` | 5 | 1.0 | **2** | 1.50 | $500.00 | True |
| `health-system-economic-valuation` | 2 | 1.5 | **2** | 1.50 | $750.00 | True |
| `multimorbidity-complexity-stratification` | 2 | 1.0 | **2** | 1.50 | $500.00 | True |
| `australasian-transferability-node` | 2 | 1.0 | **2** | 1.50 | $500.00 | True |

## 4. Federated Node Integration (Track 004)

- **Manifest Status:** `completed`
- **Synthetic Assurance:** `True`
- **Suppressed Small Cells:** `2`

## 5. Methodological Limitations

- All inputs, links, and outputs are synthetic reference artefacts for software assurance.
- Estimands model administrative linked data and are not calibrated to clinical care.
- Small-cell suppression enforces fail-closed export boundaries.
- No empirical clinical, patient, or population conclusions are made.
