# Paediatric rare-disease economic input specification

## 1. Objective

Specify the linked administrative-data cost categories and inputs for collective paediatric rare-disease burden modeling (supporting Track 012).

## 2. Linked administrative cost categories

1. **Inpatient admissions (Admitted Patient Care):**
   - Diagnosis-related group (DRG) cost weights, length of stay, intensive care unit (PICU/NICU) hours, and emergency re-admissions.
2. **Outpatient and specialist clinics (Non-admitted):**
   - Multidisciplinary paediatric clinics, genetics consultations, developmental assessments, and specialist nurse navigators.
3. **Emergency department attendances:**
   - Triage category, acute presentations, and emergency stabilization episodes.
4. **Pharmaceutical and therapeutic benefits:**
   - Orphan drugs, specialised enteral nutrition, compounding pharmacy, and immunosuppressive therapies.
5. **Special education and developmental disability services:**
   - Early childhood intervention, school learning aides, speech pathology, and occupational therapy.

## 3. Linkage and disclosure safeguards

- Deterministic and probabilistic data linkages must be conducted inside authorized secure environments (e.g. state/provincial health data linkage units).
- Small-cell counts (<5) and individual-level billing data must never be exported or committed to the open repository.
- Parameter extraction must produce aggregated, disclosure-safe mean cost and uncertainty distributions per disease code/category.
