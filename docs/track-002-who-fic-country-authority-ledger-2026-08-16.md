# WHO-FIC and national ICD authority discovery ledger — 2026-08-16

**Purpose:** Record a bounded, official-source discovery inventory for WHO-FIC
classifications outside the authenticated ICD API subset and for selected
national ICD modification, translation and adoption authorities.

**Status:** Metadata/hash-only repository evidence. It is not a global census,
licence grant, classification archive or production activation.

## Machine-readable evidence

- Source ledger:
  `manifests/classifications/who-fic-authority-sources-2026-08-16.json`
- Dated landing-page observations:
  `manifests/classifications/who-fic-authority-observations-2026-08-16.json`
- Deterministic observer: `scripts/observe_who_fic_authorities.py`

The ledger records classification, country or area, language state, version or
release state, accountable authority, official source URL, terms state and
safe archive route for 20 entries. Twelve cover WHO-FIC reference,
derived/related or retired classifications; eight cover selected country
authorities or national-use routes.

## WHO-FIC findings

- WHO names ICD, ICF and ICHI as its three reference classifications.
- The 2026-01 authenticated API evidence provides release-level ICF languages;
  the public ICF page says ICF-CY has been fully merged into ICF and should no
  longer be used.
- WHO reports ICHI Beta-3 from October 2020 and says its public-health component
  was finalized in 2023. The page says ICHI uses the ICD-11 licensing posture,
  but exact artifact/version terms still require disposition.
- WHO identifies ICD-O-3.2 (2019), ICD-O-3.1 (2013) and ICD-O-3 (2000), lists
  14 published languages, and says CSV files are available in its download
  area. No bytes are acquired because exact download and partner rights remain
  unresolved.
- The related-classification routes include ICPC, ICECI, ISO 9999, ATC/DDD,
  ICNP, verbal-autopsy standards and ICD-10-SMoL. Partner-owned systems remain
  metadata-only. The live SMoL route identifies version 2.1.

Official evidence routes include:

- <https://www.who.int/standards/classifications/>
- <https://www.who.int/classifications/international-classification-of-functioning-disability-and-health>
- <https://www.who.int/standards/classifications/international-classification-of-health-interventions>
- <https://www.who.int/standards/classifications/other-classifications/international-classification-of-diseases-for-oncology>

## Country-authority findings

The bounded seed records official routes for:

- US ICD-10-CM — CDC/NCHS;
- Australian ICD-10-AM/ACHI/ACS — IHACPA;
- Canadian ICD-10-CA/CCI — CIHI;
- German ICD-10-GM — BfArM;
- England's ICD-10 5th Edition national coding standards — NHS England;
- Dutch ICD-10 translation and maintenance — RIVM WHO-FIC Collaborating
  Centre;
- Swedish ICD-10-SE — Socialstyrelsen; and
- New Zealand's observed ICD-10-AM use — Ministry of Health/Health New Zealand.

These are not equivalent states. US, Australian, Canadian and German entries
identify national modifications or product families; England adds national
coding standards to the WHO base; the Netherlands is a translation/maintenance
authority; Sweden maintains ICD-10-SE; New Zealand is recorded as an adopter of
an Australian product, not its redistribution authority.

## Retrieval evidence and blockers

The sequential live observation on 2026-08-16 returned HTTP 200 for 19 of 20
official landing pages. The CDC landing page returned HTTP 403 to the bounded
standard-library observer; browser/search evidence confirms the official route,
but the ledger preserves the automated-access failure and does not infer file
availability from it.

Known access and rights gates remain:

- IHACPA states that classification product use by countries requires a licence
  agreement.
- CIHI exposes read-only non-commercial access and product-specific terms.
- BfArM states that downloading creates a usage contract.
- NHS classification datafiles route through TRUD and WHO content is included
  for UK purposes.
- partner-owned WHO-related classifications require their partner terms.
- no portal login, click-through, purchase or licence agreement was automated.

## Completeness boundary

The ledger does not enumerate all WHO Member States, every national ICD
modification, all translations, all historical editions, subnational
authorities or every WHO-FIC partner release. It provides deterministic seeds
and explicit next routes. The existing parent task remains open until broader
country/language discovery and SNOMED national-edition coverage are completed.
