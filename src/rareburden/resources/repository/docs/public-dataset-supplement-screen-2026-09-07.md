# Public dataset supplement screen — 2026-09-07

This is a source-screening record for real aggregate data. It does not activate
any empirical parameter, authorize controlled-data use, or claim that a source
supports an estimand without source-specific qualification.

## Recommended primary path

Track 011 should first qualify Australian Institute of Health and Welfare
(AIHW) bronchiectasis aggregates: hospitalisations, emergency presentations,
deaths, and available age/sex breakdowns. The candidate is suitable for a
bounded real-data demonstrator of observed service-use and mortality burden,
subject to recording the exact release/table, retrieval receipt, licence,
transformation, ICD/case definition, suppression and limitations.

UN World Population Prospects 2024 is a compatible denominator source for age,
sex and calendar-year population estimates. It can support rate construction
only after geography, period and age-band compatibility are explicitly bound.

## Supplementary candidates

| Source | Potential use | Current disposition |
|---|---|---|
| WHO Mortality Database | Aggregate cause-of-death comparison by country, year, sex and age | Qualify ICD definition, country coverage, revision and rights before use |
| Orphadata epidemiology | Rare-disease prevalence/incidence candidates for paediatric or rare-disease demonstrators | Disease-specific study-population, period, ascertainment and comparability review required |
| AIHW chronic-condition and linked-data reports | Australian hospitalisation, emergency and mortality context | Use only the exact published aggregate series; do not infer prevalence |
| UN WPP 2024 | Age/sex/geography denominators and stratification | Recommended denominator source; bind exact download and revision |
| World Bank population indicators | Cross-check or fallback population denominators | Supplementary cross-check only; do not silently mix revisions |

## Other demonstrators

The same sources can supplement Tracks 012 and 014 for paediatric denominator,
mortality, geography and API/release examples. They do not provide a universal
paediatric rare-disease cohort, individual-level linkage, cost data or clinical
validation. Australian rare-disease reporting also warns that most rare
diseases are not captured in routine health information systems or registries;
absence of a public series is therefore a documented data gap, not evidence of
zero burden.

## Required next evidence

For each selected source, retain the URL, publisher, release/version, retrieval
timestamp, licence/redistribution assessment, file or table hash, extraction
query, transformation code, case definition, denominator, uncertainty and
known coverage limitations. Keep empirical activation false until the exact
candidate passes the Track 003/009/011 qualification and review gates.
