# Track 002 internal review — Public-source acquisition

**Review date:** 2026-07-27  
**Decision:** Internal implementation passes for autonomous handoff; production/live-source approval remains open

## Passed internal evidence

- Network access is opt-in and bounded by HTTPS, host, address, size, timeout and redirect controls.
- Expected checksums are required by default and changed bytes fail closed.
- Manual registration supports sources whose terms or interfaces should not be automated.
- Acquisition URLs are credential-redacted before provenance is written.
- Source-release, acquisition and normalisation records are content-addressed.
- Synthetic adapters cover Orphadata-style XML, UN-style population CSV, WHO-style aggregate CSV and World Bank responses.
- Normalised rows retain source-release, acquisition and transformation lineage.
- The synthetic reference workflow executes offline and its release passes independent verification.
- The current handoff branch passed the complete local harness with 275 tests, 90.43% branch coverage and the critical-coverage policy.
- A clean single-branch clone of `track/002-release-harness` passed `uv sync --frozen --extra dev` and `make check`; distributions built from that clone were installed into separate empty environments, where both the wheel and source archive passed `rareburden validate-programme`.
- Commit `c5e50b2` aligns CLI licence states with the source-release schema, requires evidence or rationale appropriate to each state, and rejects unknown or restricted rights before automated network acquisition. The policy is internally verified only; live terms and source-change exercises remain open.
- Commit `97421ca` adds a schema-valid, credential-redacted `review_required` incident record for pinned checksum changes. Failed downloads still commit no source bytes or acquisition manifest; live-source exercise evidence remains open.

## Open blocking evidence

- Verify each live endpoint and current terms with dated evidence.
- Record redistribution and archival permissions source by source.
- Obtain data-governance and scientific review of production source choices.
- Exercise live source-change and licence-uncertainty incident paths.

## Disposition

Keep Track 002 **In review**. The substrate may be extended, tested and used with synthetic or explicitly lawful fixtures. Do not call the track complete or issue v0.3.0 until the live-source and governance gates are evidenced.

## Review fixes

- Refreshed the stale internal test and coverage counts above.
- Kept live-source, licensing, scientific and data-governance items explicitly open; repository validation cannot satisfy those gates.
- On 2026-07-27, a bounded HTTPS `HEAD` check reached 13 catalog access URLs with HTTP 200 responses. The World Bank API catalog root returned HTTP 404; this is recorded as an endpoint-contract finding, not as evidence that a production query is usable.

### Public-source evidence refresh — 2026-07-27

The following official public pages were retrieved on 2026-07-27 and are evidence of published access/terms only (not scientific or data-governance approval):

| Source | Public evidence | Operational implication |
| --- | --- | --- |
| Orphadata | [Legal notice](https://sciences.orphadata.com/legal-notice/) and [scientific files](https://sciences.orphadata.com/orphanet-scientific-knowledge-files/) state that datasets/APIs are CC BY 4.0, with attribution/change-notice requirements; releases are described as biannual. | Candidate automated source, subject to selecting and pinning an exact release and preserving attribution. Expert Resources remain separately contracted. |
| MONDO | [Official download page](https://mondo.monarchinitiative.org/pages/download/) identifies the official repository and CC BY 4.0 licence. | Candidate ontology dependency; exact release and redistribution record still required. |
| UN WPP 2024 | [Official WPP site](https://population.un.org/wpp/) identifies the 28th edition and provides downloadable Excel outputs; [methodology](https://population.un.org/wpp/assets/Files/WPP2024_Methodology.pdf) is published separately. | Candidate population denominator; pin edition/file and retain methodology provenance. |
| WHO Global Health Estimates | [GHE page](https://www.who.int/data/global-health-estimates) publishes downloadable datasets and 2000–2021 update scope; [WHO data terms](https://www.who.int/about/policies/publishing/data-policy/terms-and-conditions) permit reuse for public-health purposes while excluding credited third-party material without permission. | Candidate aggregate source; verify exact release, purpose, third-party fields and attribution before production use. |
| World Bank Indicators | [API query guidance](https://datahelpdesk.worldbank.org/knowledgebase/articles/898599-indicator-api-queries) documents indicator requests and [API call structures](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures); [Group terms](https://www.worldbank.org/ext/en/legal/terms-conditions) state that API/data-catalog use is governed by specific incorporated terms. | Endpoint contract and applicable dataset terms must be confirmed for the exact indicator query; the catalog-root 404 remains unresolved. |

These observations strengthen the public-access/terms record but do not close the open exact-endpoint, licence-change exercise, or scientific/data-governance review gates.

### Exact endpoint probe — 2026-07-27

A second bounded HTTPS `HEAD` probe used the following concrete public URLs and a descriptive user agent; every URL below returned HTTP 200 on 2026-07-27:

| Source/role | Exact URL probed | Result |
| --- | --- | ---: |
| World Bank population indicator query (JSON, one record) | `https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?date=2000&format=json&per_page=1` | 200 |
| World Bank indicator metadata query (JSON) | `https://api.worldbank.org/v2/indicator/NY.GDP.MKTP.CD?format=json` | 200 |
| Orphadata release catalogue | `https://sciences.orphadata.com/orphanet-scientific-knowledge-files/` | 200 |
| MONDO downloads | `https://mondo.monarchinitiative.org/pages/download/` | 200 |
| UN WPP landing/download route | `https://population.un.org/wpp/` | 200 |
| WHO GHE landing/download route | `https://www.who.int/data/global-health-estimates` | 200 |
| WHO data terms | `https://www.who.int/about/policies/publishing/data-policy/terms-and-conditions` | 200 |
| World Bank Group terms | `https://www.worldbank.org/ext/en/legal/terms-conditions` | 200 |

The World Bank root catalog URL in the source catalogue (`https://api.worldbank.org/v2/`) still returned 404 in the earlier probe. The successful indicator calls show a usable documented query shape, but do not select a production indicator, prove its current value coverage, or replace source-specific terms review. Exact downloadable file URLs and release hashes for Orphadata, UN WPP and WHO GHE remain to be pinned before production acquisition.

### External reviewer packet

- **Source/terms decision:** approve, narrow or reject each exact endpoint/file; require URL, release/version, retrieval date, SHA-256, licence/terms, attribution and redistribution position.
- **Scientific decision:** confirm source choice, denominator meaning, coverage, update cadence, units/metrics and known bias; record approved use and limitations.
- **Data-governance decision:** confirm lawful purpose, third-party restrictions, retention/cache rules and the changed/uncertain-terms incident path.
- **Evidence required:** attributable review record linked to exact source-release and acquisition-manifest IDs; unresolved items remain blockers.

### Bounded source inventory — v0.1.0 (retrieved 2026-07-27)

This inventory is complete as a candidate register for the Track 002 scope. A candidate is not production-approved until its exact file/query, release hash and terms position are recorded.

| Source ID | Candidate artifact or endpoint | Access class | Licence/terms route | Inventory status and next evidence |
| --- | --- | --- | --- | --- |
| `orphadata-science` | [Orphadata Science files](https://sciences.orphadata.com/orphanet-scientific-knowledge-files/), including the July 2026 release catalogue and epidemiology product route | open download/API | [Orphadata legal notice](https://sciences.orphadata.com/legal-notice/) and CC BY 4.0 | Catalogue terms PDF retrieved 2026-07-29 (975,407 bytes; SHA-256 `47b7d325cb9aa115cc639ed0045032a95c894f2315c8a20cd5bdafa70d26bf01`); exact epidemiology/alignment file still requires selection and approval. |
| `mondo-disease-ontology` | [MONDO official downloads](https://mondo.monarchinitiative.org/pages/download/) | open download | [MONDO download/licence page](https://mondo.monarchinitiative.org/pages/download/) | Candidate semantic dependency identified; pin ontology release and checksum before mapping use. |
| `un-world-population-prospects` | [UN WPP 2024](https://population.un.org/wpp/) and [WPP 2024 methodology](https://population.un.org/wpp/assets/Files/WPP2024_Methodology.pdf) | open download | UN publication/download terms attached to selected file | Methodology PDF retrieved 2026-07-29 (2,903,334 bytes; SHA-256 `0c98d8131e61227596fabf21328024a3c6ba05c27dcbbdbf507e5f7edd8a35c9`); exact geography/age/sex workbook still requires selection and approval. |
| `who-global-health-estimates` | [WHO GHE downloads](https://www.who.int/data/global-health-estimates), latest stated coverage 2000–2021 | open download/API | [WHO data terms](https://www.who.int/about/policies/publishing/data-policy/terms-and-conditions) | Terms page retrieved 2026-07-29 (85,005 bytes; SHA-256 `65f5bc40edce60279701653032d85ca198002fa9cca5a7f5a0de7c8bdd292029`); exact aggregate file, third-party fields and redistribution position remain open. |
| `world-bank-indicators-api` | [Population query](https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?date=2000&format=json&per_page=1); documented query shape also supports indicator metadata | public API | [World Bank Group terms](https://www.worldbank.org/ext/en/legal/terms-conditions) and [API guidance](https://datahelpdesk.worldbank.org/knowledgebase/articles/898599-indicator-api-queries) | Exact query shape reached HTTP 200; choose production indicator/country/date window and record response hash plus source-specific terms. |
| `ihme-gbd-results` / `ihme-ghdx` | [GBD Results](https://vizhub.healthdata.org/gbd-results/) and [GHDx](https://ghdx.healthdata.org/) | registered/manual | IHME dataset/user agreement | Manual registration only; no automated acquisition or redistribution claim. |
| `oecd-data-explorer` | [OECD Data Explorer](https://data-explorer.oecd.org/) | public/registration depending on dataset | OECD terms and conditions | Manual release registration; no automated acquisition until dataset terms and API/export behaviour are reviewed. |

The inventory separates candidate discovery from production selection. The remaining Track 002 task is exact artifact/file selection and release hashing for the open-download sources, not further source discovery.

### Decision worksheet — non-binding candidate pins (v0.1.0, 2026-07-29)

These are implementation-ready candidates for reviewer confirmation; they do not activate acquisition or freeze a contract.

| Source | Proposed pin for review | Why this is the smallest useful choice | Required confirmation before activation |
| --- | --- | --- | --- |
| Orphadata | One epidemiology product release plus its alignment release from the same catalogue date | Keeps disease identifiers and estimates on a single release boundary | Exact filenames/URLs, release date, CC BY attribution/change notice and redistribution allowed |
| UN WPP | WPP 2024 medium-variant national population totals, one workbook and explicitly recorded geography/year range | Supplies a denominator without importing unused age/sex tables | Workbook URL/hash, variant, geography/year scope and publication terms |
| WHO GHE | One aggregate burden release matching the approved measure/unit and 2000–2021 coverage | Avoids mixing releases or silently including credited third-party fields | Exact file URL/hash, metric/unit, third-party field exclusions and redistribution position |
| World Bank | `SP.POP.TOTL`, explicitly bounded country/year query, JSON response | Already has a reproducible query shape and content-addressed probe | Approved geography/year window, update cadence and terms/attribution review |

Until each row has a named approver and the required evidence, adapters must remain in registration/probe mode and fail closed for production acquisition.

### Scope decision — approved candidate set (2026-07-29)

The repository owner approved the recommended candidate set: a same-date Orphadata epidemiology/alignment pair; UN WPP 2024 medium-variant national totals; one WHO aggregate burden file covering the approved measure; and bounded World Bank `SP.POP.TOTL` JSON queries. This approves scope only. Exact artifact URLs, release identifiers, hashes, attribution and redistribution checks remain mandatory before activation.

The existing CLI already enforces the required World Bank bounds (`--country`, `--year-start`, `--year-end`) and canonicalises country codes, indicator and pagination parameters. Operators must supply the final geography and year window explicitly; there is no implicit “all countries/all years” production default.

### Content-addressed endpoint probe — 2026-07-29

The concrete World Bank reference query `https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?date=2000&format=json&per_page=1` returned HTTP 200. The response was 310 bytes with SHA-256 `cf007aeb8ff4078b46a28861c022c678c22b6c115b255b0f8f0c6ce58de6c5cb`. This is a reproducible endpoint probe, not approval of the indicator for production use; source selection, coverage review and terms confirmation remain open.

### Bounded World Bank reference manifest — 2026-07-29

The approved indicator was exercised with an explicit two-country, 2000–2021 query:
`https://api.worldbank.org/v2/country/AUS;NZL/indicator/SP.POP.TOTL?date=2000:2021&format=json&per_page=100&source=2`.
The response returned HTTP 200, one page, 44 observations, 8,826 bytes and
SHA-256 `7db1f222bf7b5af9b9da9b5f380cad48356b1d33c74c2666c9a96d0d7ca7ad4f`.
This is a bounded reference manifest and smoke test, not a production geography
decision or redistribution approval.

### Remaining exact-file blocker

The remaining exact-file task is blocked by publisher delivery evidence, not by
the repository implementation: the Orphadata catalogue intermittently fails
TLS retrieval from this environment, while UN WPP and WHO landing pages expose
download content through dynamic/static-site routes without stable data-file
URLs in the retrieved HTML. No guessed URL is recorded and no bulk source bytes
are downloaded. The next safe action is to record the publisher-provided exact
file URLs (or a custodian-approved manual registration) and then run the existing
checksum/manifest workflow.
