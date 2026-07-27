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
