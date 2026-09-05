# Track 013: Quality, Validation, Gap Mapping and Equity Assurance Reference Report

**Protocol ID:** `RBC-Q001`  
**Receipt ID:** `t013val-ac5c07ea08942e70fbe69cc9`  
**Created At:** `2026-09-06T00:00:00Z`  
**Intended Use:** `synthetic_assurance`  

## 1. Executive Summary and Governance Boundary

This report records the bounded demonstrator validation and uncertainty decomposition
for Phase 3 of Track 013. All calculations execute against synthetic reference fixtures
to verify software contracts and numerical stability under ADR-0005 and ADR-0009.
No empirical, clinical, population, or policy claims are made.

## 2. Monogenic Diabetes Triangulation (Track 003)

- **Primary Source:** `rbc-p002-primary` (Estimate: 2000.0)
- **Tolerance:** `0.15`

| Comparator Source | Estimate | Abs Diff | Rel Diff | Within Tolerance |
|---|---|---|---|---|
| `rbc-p002-model_eligibility` | 1000.0 | 1000.0 | 0.500 | False |
| `rbc-p002-age_stratified` | 2480.2 | 480.2 | 0.240 | False |
| `rbc-p002-carrier_penetrance` | 2000.0 | 0.0 | 0.000 | True |

## 3. Bronchiectasis Triangulation (Track 011)

- **Primary Source:** `rbc-p003-primary` (Estimate: 700.0)
- **Tolerance:** `0.15`

| Comparator Source | Estimate | Abs Diff | Rel Diff | Within Tolerance |
|---|---|---|---|---|
| `rbc-p003-proportional-overlap` | 742.0 | 42.0 | 0.060 | True |
| `rbc-p003-high-overlap-multimorbidity` | 784.0 | 84.0 | 0.120 | True |
| `rbc-p003-tertiary-referral-transport` | 1027.3 | 327.3 | 0.468 | False |
| `rbc-p003-community-ascertainment-transport` | 542.2 | 157.8 | 0.225 | False |
| `rbc-p003-restricted-diagnostic-capacity` | 427.4 | 272.6 | 0.389 | False |

## 4. Paediatric and Economic Scope Validation

- **Paediatric Person Conservation:** `True`
- **Paediatric Deduplicated Children:** `2`
- **Paediatric Disclosure Suppression:** `True`
- **Economic Prototype:** `invented_component_first_demo` (experimental_unfrozen)
- **Economic Components Validated:** `3`
- **Overall Scope Verified:** `True`

## 5. Uncertainty Decomposition and Sensitivity

- **Decision-Sensitive Parameters:** `['prevalence_per_100k', 'cost_multiplier', 'diagnostic_yield']`

| Parameter | Max Relative Change | Decision Sensitive |
|---|---|---|
| `prevalence_per_100k` | 1.5000 | `True` |
| `cost_multiplier` | 0.6667 | `True` |
| `diagnostic_yield` | 0.5000 | `True` |
| `missingness_fraction` | 0.1667 | `False` |

## 6. Declared Limitations

- All inputs, comparators, and outputs are synthetic reference fixtures.
- Agreement across synthetic scenarios is a software assurance diagnostic.
- Decision sensitivity does not establish empirical validity or policy priority.
- Fail-closed boundaries prohibit empirical or clinical interpretation without lawful activation.

