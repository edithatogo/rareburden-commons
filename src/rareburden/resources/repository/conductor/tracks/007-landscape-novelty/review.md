# Track 007 internal review — Landscape, adjacency and novelty

**Review date:** 2026-07-27  
**Decision:** Proceed with narrowed scope, subject to registered review and external challenge

### Review rerun — 2026-07-29

Repository review result: **Pass with external blockers**. The seed screening
register, protocol draft, repository-native search evidence and adjacency claims
are internally consistent after the wording correction above. The full project
validation gate passes. The track remains in review because protocol registration,
broader discovery screening, independent methods review and patient/community
challenge are external or human gates.

## Internal findings

- The programme should not create another rare-disease registry, ontology, genomic repository or central patient-data lake.
- Orphanet/Orphadata, MONDO and related standards are dependencies for the semantic layer, not competitors to replace.
- IHME/GBD and WHO estimates can provide broad burden envelopes but do not presently constitute a transparent global rare-disease attribution layer.
- Genomic programmes, registries and administrative datasets can estimate complementary parameters without requiring patient-level linkage across platforms.
- The strongest provisional niche is a federated measurement, provenance and policy-translation layer that exposes uncertainty, overlap, evidence quality and non-estimability.

## Evidence limitations

- The current 13-item register is a rapid structured landscape, not a completed systematic or scoping review.
- Repository-native discovery searches and mechanical exact deduplication are recorded; the 13-record seed catalogue now has an auditable screening/exclusions register, while broader discovery screening remains incomplete.
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

A mechanical catalogue deduplication pass on 2026-07-27 found 13 initiatives, 13 unique `initiative_id` values and 13 unique official URLs. This confirms no exact identifier/URL duplicates in the current register; it is not a substitute for title/entity screening or cross-registry deduplication of newly discovered records.

### Versioned draft search and screening protocol — RBC-LAND-007 v0.1.0 (2026-07-27)

This is a repository-native draft prepared for external registration; it is not itself a registered protocol or completed systematic review.

**Question.** Which public rare-disease burden, registry, ontology, genomic, policy, standards and methodological infrastructures overlap with or complement a federated measurement/provenance/policy-translation layer, and what documented gap or boundary remains?

**Sources and search strings.** Search each source on the retrieval date using the exact strings below, preserving the raw URL, timestamp, HTTP status, result total (where provided), and first-page identifiers:

1. GitHub repository search API: `rare disease burden`, `rare disease registry`, `rare disease ontology`, `rare disease prevalence`, `rare disease cost`.
2. Zenodo records API: the same five strings, with fielded follow-up searches for `title`, `description`, `metadata.subjects` and `communities`.
3. OSF nodes API: title filters for each string, followed by broader public search if the exact-title result is zero.
4. Hugging Face datasets API: each string plus `rare disease`, `burden`, `registry` and `ontology` as separate terms.
5. Cited official institutional and scholarly sources in `catalog/initiatives.yml`, searched by initiative name, alternate name and official domain.

**Eligibility.** Include a record when it is publicly identifiable, has a stable landing page or persistent identifier, and materially contributes a rare-disease burden estimate, registry/data infrastructure, ontology/standard, policy mandate, or method relevant to measurement, provenance, uncertainty, equity or governance. Include both potential overlap and foundational dependency. Exclude purely clinical guidance with no measurement/data relevance, individual case reports, non-public systems with no inspectable description, duplicate versions of the same initiative, and records whose only relation is a generic rare-disease mention.

**Screening workflow.** Export discovery metadata; normalize title, canonical URL/DOI, organisation and year; perform exact identifier/URL deduplication; then perform manual entity-level deduplication across alternate names and versions. Screen title/abstract/landing metadata, record include/exclude/uncertain plus a one-line reason, and resolve uncertain records by a second reviewer. Extract the existing catalogue fields, preserve excluded records in an exclusions table, and record a change log whenever eligibility or search strings change. Report counts at discovery, after exact deduplication, after entity deduplication, screened, included, excluded and awaiting resolution.

**Bias and limits.** API totals are time-sensitive; English-language and public-web bias, ranking bias, missing metadata, duplicate releases and inaccessible proprietary systems may affect completeness. The result is an adjacency and gap map, not evidence of partnership, endorsement, data access or scientific superiority. External registration, independent methods review and patient/community challenge remain required.

### External reviewer packet

- **Methods decision:** accept, revise or reject the search question, strings, eligibility rules, deduplication and exclusion reasons; require the registered protocol identifier and reproducible exports.
- **Patient/community decision:** assess relevance, harms, language, equity and acceptable interpretation; record approval, requested narrowing or dissent.
- **Programme decision:** approve only bounded adjacency/gap claims; prohibit partnership, endorsement or access claims without documentary evidence.
- **Evidence required:** protocol registration, dated search logs, deduplication/exclusions table, reviewer comments and a claim-to-source map.

### Preliminary screening baseline — 2026-07-27

The seeded catalogue provides an auditable starting screen of 13 records. All 13 are provisionally **include for adjacency review** because each has a stable official URL, a documented contribution type, and a stated RareBurden relationship in `catalog/initiatives.yml`. The baseline counts are: discovered 13; exact-duplicate removals 0; entity-level duplicate removals 0; provisionally included 13; excluded 0; uncertain 0. This is a seed-catalogue screen, not a completed search screen: newly discovered records, alternate names, full-text eligibility and independent second-review resolution remain outstanding. The exclusions log therefore remains open and must record later exclusions rather than treating this zero baseline as proof that no exclusions exist.

The seed baseline is now preserved in [`docs/landscape-screening-007.md`](../../../docs/landscape-screening-007.md) as `RBC-LAND-007-SCREEN v0.1.0`. It records all 13 decisions, duplicate keys, reasons and explicit zero-exclusion counts. This closes the seed-catalogue evidence gap without representing the broader search as complete.

### Authenticated OSF route check — 2026-07-29

Using the installed `osf-cli-go` username/password authentication path, `osf auth whoami` and `osf projects list --json` succeeded. The CLI command `osf search "rare disease burden" --json` reached `/v2/search/?q=rare+disease+burden` but OSF returned HTTP 404. A documented API fallback query to `/v2/nodes/?filter[title]=rare%20disease%20burden&page[size]=10` returned HTTP 200 with `total=0`. This is an OSF endpoint-compatibility finding, not evidence that no relevant OSF work exists; broader search remains open. No library code was changed or submitted.

### Bounded discovery rerun — 2026-08-01

The four repository-native discovery routes were rerun with the versioned query
`rare disease burden`, a descriptive user agent, and a 30-second timeout. These
observations refresh the discovery log only; they do not screen records,
establish novelty, or replace the required registered protocol and second
reviewer.

| Registry | Endpoint | HTTP | Result observation |
| --- | --- | ---: | --- |
| GitHub repositories | `https://api.github.com/search/repositories?q=rare%20disease%20burden&per_page=10` | 200 | `total_count=6`, 6 first-page items |
| Zenodo records | `https://zenodo.org/api/records/?q=rare%20disease%20burden&size=10` | 200 | `hits.total=193121`, 10 first-page records |
| OSF nodes | `https://api.osf.io/v2/nodes/?filter%5Btitle%5D=rare%20disease%20burden&page%5Bsize%5D=10` | 200 | `data=[]`; exact-title route returned no nodes |
| Hugging Face datasets | `https://huggingface.co/api/datasets?search=rare%20disease%20burden&limit=10` | 200 | 0 datasets returned |

The changed totals demonstrate why search counts are retrieval-date evidence,
not fixed catalogue facts. Newly returned records remain unscreened and are not
added to the initiative register until the registered eligibility workflow and
independent resolution process are completed.
