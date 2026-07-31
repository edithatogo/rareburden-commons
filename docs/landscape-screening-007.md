# Track 007 screening and exclusions register

**Register:** `RBC-LAND-007-SCREEN v0.1.0`  
**Screen date:** 2026-07-29  
**Input:** `catalog/initiatives.yml` (13 seed records)  
**Screen type:** reproducible seed-catalogue baseline; not a completed systematic review

## Decision rules

Include records with a stable official landing page and a material contribution to
rare-disease burden estimation, registry/data infrastructure, ontology/standard,
policy mandate, or methods relevant to provenance, uncertainty, equity or
governance. Exclude generic mentions, individual case reports, inaccessible
systems without an inspectable description, and duplicate entities or releases.
Use `uncertain` when the landing metadata are insufficient for a confident decision.

## Seed screen

| Record | Canonical URL | Decision | Reason | Duplicate key |
|---|---|---|---|---|
| `who-rare-disease-action-plan` | https://www.who.int/health-topics/rare-diseases | include | Policy mandate with measurable implementation relevance | `who-rare-disease-action-plan` |
| `rdi-lancet-commission` | https://www.rarediseasesinternational.org/ | include | Patient-led global burden/policy synthesis | `rdi-lancet-commission` |
| `wef-rare-disease-data` | https://www.weforum.org/ | include | Cross-sector rare-disease data and economic policy agenda | `wef-rare-disease-data` |
| `orphadata` | https://www.orphadata.com/ | include | Open disease knowledge and epidemiology dependency | `orphadata` |
| `mondo` | https://mondo.monarchinitiative.org/ | include | Ontology and semantic mapping dependency | `mondo` |
| `ihme-gbd` | https://www.healthdata.org/gbd | include | Broad burden-estimation methodological comparator | `ihme-gbd` |
| `who-ghe` | https://www.who.int/data/global-health-estimates | include | Aggregate health-estimate comparator | `who-ghe` |
| `erdera-virtual-platform` | https://www.erdera.org/ | include | Federated rare-disease research infrastructure | `erdera-virtual-platform` |
| `rd-connect` | https://rd-connect.eu/ | include | Registry/genomics/data-integration infrastructure | `rd-connect` |
| `ga4gh` | https://www.ga4gh.org/ | include | Genomic data standards and governance precedent | `ga4gh` |
| `all-of-us` | https://allofus.nih.gov/ | include | Large-scale data governance and methods comparator | `all-of-us` |
| `genomics-england` | https://www.genomicsengland.co.uk/ | include | National genomic infrastructure comparator | `genomics-england` |
| `western-australia-rare-disease-burden` | https://www.health.wa.gov.au/ | include | Jurisdictional burden and policy implementation comparator | `western-australia-rare-disease-burden` |

## Counts and exclusions

| Stage | Count |
|---|---:|
| Discovered in seed catalogue | 13 |
| Exact identifier/URL duplicates removed | 0 |
| Entity duplicates removed | 0 |
| Screened | 13 |
| Included for adjacency review | 13 |
| Excluded | 0 |
| Uncertain / awaiting resolution | 0 |

The zero-exclusion result is an explicit baseline, not evidence that the broader
repository-native or scholarly search will have no exclusions. Newly discovered
records must be appended with a stable identifier, canonical URL, decision,
reason, reviewer and screening date; records are never deleted to hide an
exclusion.

## Open boundaries

- Broader API and scholarly discovery exports still require screening against the
  registered strategy.
- Cross-registry entity resolution and second-reviewer resolution remain open.
- External protocol registration, independent methods review and patient/community
  challenge remain required before final novelty claims.
