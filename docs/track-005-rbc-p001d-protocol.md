# RBC-P001D economic and social burden protocol

**Version:** 1.0.0 (non-binding preparation; reference methods and software contract)  
**Status:** complete for bounded synthetic reference methods; empirical activation and human survey administration remain deferred under a fail-closed gate.

This protocol defines the formal methods and software contract for economic and social burden modeling in RareBurden Commons, per Track 005 and ADR-0009.
Synthetic calculations are reference outputs only and must be labelled non-empirical; no universal monetary burden is claimed.

## 1. Perspectives

Analyses must report each declared perspective separately before any comparison or aggregation:

- **Health-system perspective:** direct medical, diagnostic, therapeutic, and formal healthcare/social-care resources paid by public health authorities, statutory schemes, or health insurers. Transfer subsidies paid by the health system are expenditures; patient co-payments received are cost reductions.
- **Household perspective:** out-of-pocket spending, uncompensated travel/accommodation, and unpaid caregiver/family time. Direct disability or cash transfer payments received by households are credits; taxes are out-of-scope.
- **Societal perspective:** real resource consumption across the health system, households, education, and wider economy. Pure intra-societal transfer payments (e.g. government disability cash grants to families) are resource redistributions and must be excluded from the aggregate societal resource-cost total to prevent double-counting, while remaining reported in distributional tables.

Every component must declare its perspective, payer, bearer, recipient, beneficiary, time provider, population context, geography, observation period, unit, and denominator basis.

## 2. Component taxonomy

The reference taxonomy partitions rare disease burden into discrete modules:

1. **Direct medical:** inpatient admissions, outpatient consultations, emergency attendances, specialist diagnostics, pharmaceuticals, surgical interventions, medical devices, and allied health.
2. **Direct non-medical:** patient and family transport, accommodation for clinical visits, home/vehicle modifications, specialised equipment, and dietary requirements.
3. **Formal social care:** statutory social work, respite facilities, community nursing, and professional personal assistance.
4. **Caregiver and household time:** informal care hours provided by family/unpaid caregivers for activities of daily living, supervision, and clinical coordination.
5. **Productivity loss:** absenteeism, presenteeism, early retirement, reduced hours, and premature mortality among individuals living with a rare disease and working-age family caregivers.
6. **Education impact:** special educational needs support, schooling days missed, delayed educational milestones, and educational adjustments.
7. **Social participation:** civic and recreational exclusion, leisure restriction, and caregiver isolation.

## 3. Valuation and adjustment contract

Every monetary valuation requires explicit caller-supplied parameters without hidden defaults:

- **Currency and price year:** all monetized quantities must specify ISO 4217 currency and price year.
- **Price adjustment (inflation):** converting between price years requires an explicit deflator/index rate and source provenance.
- **Currency conversion / PPP:** converting between currencies requires an explicit exchange rate or purchasing-power parity (PPP) conversion factor and rate provenance.
- **Discounting:** multi-year cost streams require an explicit annual discount rate (e.g., 0.03 or 0.05) and discounting convention (`end_of_period`, `beginning_of_period`, or `continuous`).
- **Transfer payment accounting:** transfer payments must identify payer and recipient, and must not be added into societal resource consumption totals.
- **Unvalued resources:** unpaid care hours and educational gaps must remain visible in their natural nonmonetary units (hours, days) alongside monetary values. When unvalued, they must be recorded as nonmonetary quantities or visible data gaps, never converted silently to zero cost.

## 4. Overlap and missingness rules

To prevent double counting across fragmented datasets:

- Each component must record an overlap assessment status: `assessed_no_overlap`, `possible_overlap`, `unassessed`, or `not_applicable`.
- Possible or unassessed overlap blocks aggregation.
- Aggregation is permitted only among components assessed as `assessed_no_overlap` that share identical perspective, unit, denominator basis, population, geography, and observation period.
- Missingness must use explicit states: `explicit_value`, `explicit_zero`, `missing`, `not_collected`, `unassessed`, or `not_applicable`. Missing data must never be imputed silently as zero.

## 5. Survey core protocol and fail-closed collection gate

Per owner completion Route A:
- A standardized patient/family survey core is specified for future collection.
- Any attempt to administer the survey, recruit human participants, or ingest unapproved survey records is blocked by an executable fail-closed collection gate (`check_collection_gate`).
- The collection gate requires cryptographic verification of:
  1. institutional human research ethics committee (HREC/IRB) approval identifier;
  2. participant information, informed consent, and withdrawal protocol;
  3. participant remuneration schedule ensuring no uncompensated community labour;
  4. accessibility and linguistic adaptation register; and
  5. data custodian authorization.

## 6. Equity and distributional reporting

Analyses must report who bears costs (households vs public health systems vs employers) and how burden is distributed across subgroups (age brackets, geographic areas, disease severities, socio-economic strata).
