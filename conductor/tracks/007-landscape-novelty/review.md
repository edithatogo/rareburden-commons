# Track 007 internal review — Landscape, adjacency and novelty

**Review date:** 2026-07-27  
**Decision:** Proceed with narrowed scope, subject to registered review and external challenge

## Internal findings

- The programme should not create another rare-disease registry, ontology, genomic repository or central patient-data lake.
- Orphanet/Orphadata, MONDO and related standards are dependencies for the semantic layer, not competitors to replace.
- IHME/GBD and WHO estimates can provide broad burden envelopes but do not presently constitute a transparent global rare-disease attribution layer.
- Genomic programmes, registries and administrative datasets can estimate complementary parameters without requiring patient-level linkage across platforms.
- The strongest provisional niche is a federated measurement, provenance and policy-translation layer that exposes uncertainty, overlap, evidence quality and non-estimability.

## Evidence limitations

- The current 13-item register is a rapid structured landscape, not a completed systematic or scoping review.
- Repository-native searches, deduplication and exclusions are incomplete.
- No independent methods or patient/community reviewer has yet challenged the novelty conclusion.
- Partnership, endorsement and data-access claims remain prohibited without written confirmation.

## Disposition

Keep Track 007 **In review**. Use `proceed_with_narrowed_scope` as a provisional programme decision only. Complete registration, searches and external challenge before the final v0.3.0 gate.

## Review fixes

- Confirmed the catalogue contains 13 initiatives and remains a rapid internal landscape.
- Kept protocol registration, repository-native searches, deduplication/exclusions, and independent methods and patient/community challenge explicitly open.
- Kept partnership, endorsement, data-access, and final novelty claims bounded by documentary evidence.

### Repository-native search evidence — 2026-07-27

To make the next screening pass reproducible, the following bounded public API searches were run with the query `rare disease burden` and a descriptive user agent. HTTP status and result totals are recorded; these are discovery results, not screened inclusions or novelty conclusions.

| Registry | Query endpoint | HTTP | Result observation |
| --- | --- | ---: | --- |
| GitHub repositories | `https://api.github.com/search/repositories?q=rare%20disease%20burden` | 200 | `total_count=5` |
| Zenodo records | `https://zenodo.org/api/records/?q=rare%20disease%20burden&size=10` | 200 | `hits.total=192233` (broad full-text search; requires fielded screening) |
| OSF nodes | `https://api.osf.io/v2/nodes/?filter%5Btitle%5D=rare%20disease%20burden` | 200 | `total=0` for exact title filter |
| Hugging Face datasets | `https://huggingface.co/api/datasets?search=rare%20disease%20burden&limit=10` | 200 | 0 returned datasets |

Official API documentation used to select these routes: [Zenodo search guide](https://zenodo.org/help/search), [Zenodo developers](https://developers.zenodo.org/), and [OSF API v2 documentation](https://developer.osf.io/). Search totals are time-sensitive and must be rerun at screening; deduplication, exclusions, protocol registration, and independent methods/patient-community challenge remain open.
