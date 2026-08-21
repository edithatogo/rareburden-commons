# RareBurden public-data capability and evidence-gap map

> This is an access-capability map, not evidence that a source is complete,
> representative, transportable or analytically sufficient.

Catalogue: schema `0.1.0`, updated `2026-08-21`.

| Need | Domain | Scope | Access | Readiness | Matching sources |
|---|---|---|---|---|---|
| Population denominators | `population` | Global and country | `public_open` | `metadata_reviewed` | un-world-population-prospects, world-bank-indicators-api |
| Mortality envelopes | `mortality` | Global and country | `public_open` | `metadata_reviewed` | ihme-gbd-results, who-global-health-estimates |
| Health-loss envelopes | `health_burden` | Global and country | `public_open` | `metadata_reviewed` | ihme-gbd-results, who-global-health-estimates |
| Individual healthcare utilisation | `electronic_health_record` | Country or cohort | `controlled_access_required` | `metadata_reviewed` | all-of-us-researcher-workbench, genomics-england-research-environment |
| Rare-disease semantic definitions | `ontology` | Global | `public_open` | `metadata_reviewed` | mondo-disease-ontology, orphadata-science, umls-metathesaurus |
| Household economic and social burden | `economic_social` | Country and patient/family | `unavailable` | `unavailable` | None matching |

## Limitations

- A catalogue match is not evidence of completeness, representativeness, transportability or analytical sufficiency.
- Access conditions and licences require source-specific verification.
