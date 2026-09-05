# Track 011: Bronchiectasis Rare-Aetiology Demonstrator Reference Report

**Protocol ID:** `RBC-P003`  
**Receipt ID:** `demo11-a03a789122c0e02b70861ec7`  
**Created At:** `2026-09-05T00:00:00Z`  
**Status:** Synthetic reference analysis; no empirical validation or clinical authority.

## 1. Executive Summary

This report records the executed synthetic reference analysis for Track 011 (`011-bronchiectasis-demonstrator`) under protocol RBC-P003. The demonstrator models a common-disease respiratory phenotype (bronchiectasis) containing multiple rare aetiologies (e.g. primary ciliary dyskinesia, cystic fibrosis, primary immunodeficiencies), multi-aetiology overlap, and substantial unexplained (idiopathic) proportions.

## 2. Conservation Accounting

| Quantity | Cases | Description |
|---|---|---|
| Denominator | 1000.0 | Synthetic population envelope |
| Mutually Exclusive Sum | 700.0 | Conserved exclusive subgroup sum |
| Multi-Aetiology Cases | 80.0 | Separate non-summable structural bucket |
| Unknown / Idiopathic | 150.0 | Unclassified / uninvestigated bucket |
| Unaccounted Remainder | 70.0 | Exact conservation remainder |

**Conservation Check Passed:** `True`

## 3. Evaluated Scenarios and Structural Sensitivity

| Scenario ID | Multi Fraction | Unknown Fraction | Transport Mult | Attributable Cases | Denom Proportion | Exacerbations | Treatment Eligible |
|---|---|---|---|---|---|---|---|
| `baseline-primary-exclusive` | 0.0 | 0.0 | 1.0 | **700.0** | 0.7000 | 560.0 | 560.0 |
| `proportional-overlap` | 0.25 | 0.1 | 1.0 | **742.0** | 0.7420 | 667.8 | 608.44 |
| `high-overlap-multimorbidity` | 0.5 | 0.2 | 1.0 | **784.0** | 0.7840 | 940.8 | 666.4 |
| `tertiary-referral-transport` | 0.35 | 0.15 | 1.35 | **1027.35** | 1.0274 | 1541.03 | 924.62 |
| `community-ascertainment-transport` | 0.15 | 0.05 | 0.75 | **542.25** | 0.5423 | 325.35 | 379.57 |
| `restricted-diagnostic-capacity` | 0.1 | 0.02 | 0.6 | **427.44** | 0.4274 | 299.21 | 277.84 |

## 4. Reference Range

- **Minimum Estimated Attributable Cases:** `427.44` (42.74% of denominator)
- **Maximum Estimated Attributable Cases:** `1027.35` (102.73% of denominator)

## 5. Methodological Limitations

- All inputs and outputs are synthetic reference artefacts for software assurance.
- Scenario allocations are structural model assumptions, not empirical medical evidence.
- Transport multipliers model hypothetical transfer and are not calibrated to any clinical jurisdiction.
- No clinical diagnosis, patient prognosis, or therapeutic recommendation is made.

