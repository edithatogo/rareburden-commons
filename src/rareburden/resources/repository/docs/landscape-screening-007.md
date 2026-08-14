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

## Bounded public-API first-page screen — v0.2.0

The complete first pages returned by the five v0.2.0 query families on
2026-08-14 UTC are preserved in
`docs/track-007-search-results-2026-08-15.json`. The deterministic workflow in
`scripts/screen_track_007_results.py` records exact DOI or registry-identifier
deduplication, a public title/metadata scope screen, explicit exclusions and
unresolved exact-title entity clusters in
`docs/track-007-screening-2026-08-15.json`.

| Stage | Count |
|---|---:|
| Returned first-page occurrences | 133 |
| Exact duplicate occurrences removed | 13 |
| Unique records screened | 120 |
| Included for adjacency/full-text review | 69 |
| Excluded after title/public-metadata screen and bounded identifier resolution | 51 |
| Uncertain after bounded identifier resolution | 0 |
| Potential exact-title entity clusters | 4 |

The repository itself is excluded as a self-result. A shared DOI is the only
automatic cross-index merge key; exact normalized titles are flagged but not
merged because versions and similarly named entities may differ. “Include” is
only an invitation to adjacency/full-text review, not a final eligibility,
quality, novelty or partnership finding. This bounded screen does not cover
later result pages, all languages, private or poorly indexed resources, or the
full public web.

The sole missing-title record, DOI `10.35802/104746`, was resolved through the
Crossref persistent-identifier endpoint on 2026-08-14 UTC. The returned metadata
identified a Wellcome grant, supplied no title or rare-disease scope signal,
and was therefore excluded under the registered eligibility rules. The
timestamp, endpoint, response hash and observed fields are recorded in
`docs/track-007-screening-resolutions-2026-08-15.json`; the response bytes are
not retained. This closes uncertainty only for the bounded first-page set. It
does not complete pagination, full-text eligibility, entity resolution,
coverage or novelty assessment.

## Bounded full-text workflow status — 2026-08-15

All 69 records retained for the next stage are represented in
`track-007-fulltext-locator-observations-2026-08-15.json` and the derived
`track-007-fulltext-eligibility-2026-08-15.json`. The observation used HEAD
requests only and retained no bodies, abstracts or copyrighted full text. It
found 61 reachable and 8 access-restricted locators. These observations are
locator evidence, not eligibility decisions: 61 records remain pending content
assessment and 8 remain pending lawful access. Final exclusion requires a
registered reason and hash-bound evidence. Final novelty and all external gates
remain pending.
