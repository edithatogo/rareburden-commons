# Track 002 internal review — Public-source acquisition

**Review date:** 2026-07-27  
**Decision:** Internal implementation passes for autonomous handoff; production/live-source approval remains open

## Minimal public-release scope disposition — 2026-08-20

The repository owner narrowed public-release preparation to the exact July
2026 Orphadata pair and the three canonical MONDO `v2026-08-04` artifacts.
The machine-readable allowlist records five exact byte counts and SHA-256
digests and fails closed for WPP, WHO GHE, HPO, PanelApp, credentialed sources
and every other observed or archived source.

Review disposition: **pass for repository preparation only**. Publication,
Issue #2 closure and v0.3.0 release remain unauthorized. An earlier public
projection contains WPP and other out-of-scope objects; this is recorded as a
pending external-remediation gate, not falsely described as already private.
Live included-source terms/change evidence, candidate packaging, attribution
audit, Track 007 bounded-claims disposition and exact-candidate owner release
authority remain pending.

### Exact-candidate verification attempt — 2026-08-20

The read-only verifier passed its offline allowlist, bounded-claims,
deterministic-package, lint and type checks. Three bounded live attempts did
not produce a candidate: one ended on a non-matching `mondo.owl` stream, one
on a TLS handshake timeout during terms/metadata observation, and one after
both permitted `mondo-rare.owl` retrieval attempts timed out. Temporary source
bytes were removed after each byte-retrieval attempt.

The official GitHub release API continued to report the approved sizes and
SHA-256 values for all three MONDO assets. That metadata supports a transport
failure disposition but does not substitute for exact package-byte
verification. Review disposition: **blocked fail-closed on reproducible live
transport**. Candidate, included-source live-terms, attribution and final owner
publication gates remain pending. No upload, credential use, private capture,
activation, issue closure or publication occurred. Evidence is recorded in
`docs/track-002-minimal-candidate-verification-attempt-2026-08-20.json`.

## Private archive capacity decision review — 2026-08-16

The storage decision packet binds the exact failed Hugging Face quota receipt,
the manifest-derived 2,432-artifact historical backlog and the only observed
historical byte total (2,233,759,449 bytes for five MRCONSO artifacts). It does
not extrapolate that family to a total byte or cost estimate. The comparison
records provider-pricing observations as dated and volatile, includes storage,
request, retrieval, egress, migration, security, retention and withdrawal
tradeoffs, and authorizes no purchase, bucket creation, upload or redownload.

Review disposition: **pass for repository decision preparation**. Option C
(metadata/hash-only pause) remains the enforced immediate state. Option A
(bounded Hugging Face capacity increase) is recommended only after an exact
quote and owner cost cap; Option B (private S3-compatible storage) is a
conditional fallback when exact security, region, retention or price needs
justify migration. Every resumption path remains blocked behind the checklist,
dated expiring capacity evidence and a one-artifact canary. This review does not
restore capacity or complete the licensed historical archive.

The 2,432 count is the consolidated cross-family snapshot after those five
MRCONSO receipts. The latest full-Metathesaurus-subset family observation is
more local: 12 verified and two pending at the blocked cursor. Failed run
`31897934633` was bounded to one artifact and advanced neither the cursor nor
the consolidated checkpoint. A two-artifact continuation is only a proposed
post-canary tranche, not an observed upload or authorization.

The separate public MONDO canary `31900277331` succeeded only after the
publisher and existing remote object were reconciled as exact identical bytes.
That integrity path remains independently fail-closed and does not provide UTS
capacity evidence or change the licensed-archive storage recommendation.

### Review rerun — 2026-07-29

Repository review result: **Pass with external blockers**. The full project gate
(`uv run make check`) passes, including programme/schema/workflow validation,
runtime assets, lint/format/type checks, Markdown links, repository safety,
compileall and the test suite. No credentials, participant-level data or bulk
third-party source files are present in the tracked diff.

The track is not archive-eligible because exact Orphadata, UN WPP and WHO
production artifacts and their live licence/scientific/data-governance review
remain unresolved, and Track 007 has not completed its external challenge gate.

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

### Bounded live source-change exercise — 2026-08-20

`scripts/observe_track_002_source_change.py` re-retrieved the exact pinned
Orphadata epidemiology and alignment files, WPP 2024 workbook, WHO GHE workbook
and bounded World Bank response with one-second inter-request pacing and a
60 MB per-response ceiling. All five returned HTTP 200 and matched their pinned
SHA-256 values. The observer discarded response bytes after streaming hashes,
recorded no activation, and would classify changed or unavailable responses as
review-required incidents.

Evidence is bound in
`docs/track-002-live-source-change-exercise-2026-08-20.json`, with deterministic
and negative tests in `tests/test_track_002_live_source_change.py`. This closes
the dated live source-change exercise only. It does not establish current
publisher terms, scientific fitness, representativeness, redistribution rights
or production activation. Those decisions remain fail-closed per exact source
and estimand.

### Activation-evidence reconciliation — 2026-08-20

The activation and source-terms matrices now distinguish evidence already in
the repository from the decision still required. Agent-panel methods advice,
the 2026-08-15 owner data-use disposition and the 2026-08-20 stable-byte
exercise are recorded for Orphadata, WPP and the World Bank probe. WHO remains
candidate-only because its field-level third-party rights are unresolved.

No row is active. Orphadata still requires an exact owner activation decision
for identifier/descriptive use; WPP additionally requires named geography and
year bounds; the World Bank remains probe/cross-check only; WHO requires rights
evidence and a new owner decision. This reconciliation removes stale pending
labels without treating preparation evidence as activation authority.

### External-gate panel synthesis — 2026-08-01

The repository's preparatory panel review is recorded in
`docs/v1-subagent-panel-report-017.md` and governed by
`docs/decisions/ADR-0007-external-gate-handling.md`. It confirms that the
public/synthetic substrate is bounded for further preparation, but does not
constitute live-source licensing, scientific, data-governance or security
approval. The exact production artifact, rights and source-change exercises
listed above therefore remain open; no status transition is implied.

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

### Synthetic source-change panel exercise — 2026-08-02

The repository now runs a parametrized synthetic mutation across the Orphadata,
UN WPP, WHO GHE and World Bank candidate IDs. Each changed-byte case produces a
credential-redacted `review_required` incident, preserves the pinned release,
creates no destination bytes and prevents promotion. This demonstrates local
control behavior only; it is not a live source-change or licence exercise and
does not close the external gate.

### Finding disposition panel — 2026-08-02

`docs/track-002-finding-disposition-2026-08-02.md` classifies repository-owned
findings as closable where evidence exists and assigns scientific, custodian,
live-operator and Track 007 dependency findings to their accountable gates.
The recommended bounded source posture does not authorize activation or
archiving.

### Track 007 dependency panel — 2026-08-02

`docs/track-002-track-007-gate-disposition-2026-08-02.md` keeps the Track 007
challenge as an open release dependency, while allowing bounded repository
preparation and manifest/synthetic fallbacks. No novelty or completeness claim
is promoted and no v0.3.0 release decision follows from the panel.

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

### Exact Orphadata endpoint evidence — 2026-08-01

The July 2026 Orphadata catalogue exposes stable English XML routes. Both files
were retrieved directly from the publisher host and verified locally before this
record was written; the bytes are not committed to the repository.

| Candidate | Exact URL | Retrieved bytes | SHA-256 |
| --- | --- | ---: | --- |
| English epidemiology XML (`en_product9_prev.xml`) | `https://www.orphadata.com/data/xml/en_product9_prev.xml` | 16,178,169 | `6b492b3cc61e5a0327de12f59386a07a071760a938d0bbd8f525bc4a5f71b7f0` |
| English alignment XML (`en_product1.xml`) | `https://www.orphadata.com/data/xml/en_product1.xml` | 54,026,799 | `df8d562a0c6011af36a74eb4000ce81ca7d723e8031010819fb71727c0962bbb` |

The publisher pages identify these as the July 2026 release and state CC BY
4.0 terms. This records exact Orphadata endpoints and content hashes only; it
does not activate production acquisition or substitute for the required live
scientific/data-governance and redistribution review.

### Remaining source-approval blocker

Exact UN WPP and WHO candidate routes and hashes are now recorded below. The
remaining blocker is not route discovery: it is completion of the source
registration fields, metric/scope confirmation, licensing/redistribution
position, scientific review, data-governance review and live source-change
exercise. No production acquisition is activated until those decisions are
recorded.

### Exact UN/WHO candidate pins — 2026-08-01

Bounded read-only publisher-route checks identified stable candidate files and
streamed each response directly to a local hash process; source bytes were not
retained or committed. These are candidate pins, not production approval.

| Source | Exact candidate URL | Bytes | SHA-256 | Evidence state |
| --- | --- | ---: | --- | --- |
| UN WPP 2024 compact demographic indicators | `https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/EXCEL_FILES/1_General/WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx` | 26,142,942 | `98e34d9b65b53858cd08a57a566e45050b08093ad85ba5714fe6fbd78055ae6d` | Exact route/hash candidate; variant, scope, terms and reviewer decision open |
| WHO GHE 2021 country DALY estimates for 2000 | `https://cdn.who.int/media/docs/default-source/gho-documents/global-health-estimates/ghe2021_daly_bycountry_2000.xlsx?sfvrsn=23cd3c55_5` | 12,756,114 | `a051da530e7802ff6c084293b50e8de21cce0c36f02b76085568487f143246fe` | Exact route/hash candidate; metric scope, third-party fields, terms and reviewer decision open |

The publisher pages identify WPP 2024 as the 28th revision and WHO GHE 2021
as the 2000–2021 release family. The hash observations close the route-discovery
subtask only. They do not authorize caching, redistribution, scientific use or
production acquisition; complete the source-registration template and obtain
the required scientific and data-governance dispositions first.

Machine-readable candidate records are preserved in
`docs/track-002-un-wpp-2024-candidate.yml` and
`docs/track-002-who-ghe-2021-candidate.yml`. Their `candidate_only` decisions,
conditional licence states and pending reviewer fields are intentional.

### Repository-owner scope decision — 2026-08-02

The repository owner approved the bounded Orphadata + UN WPP preparation
posture, with WHO and World Bank candidate-only, no v0.3.0 activation, and the
Track 007 challenge retained as a release dependency. This is a scope decision,
not scientific, custodian, independent-operator or release-authority approval.

### Exact WPP/WHO terms audit — 2026-08-15

The exact WPP workbook embeds a United Nations copyright notice, CC BY 3.0 IGO
licence URL and suggested citation. Its unmodified bytes are therefore archived
in the private Hugging Face source archive at revision
`ae188ced2bced5e403e82af61990a28f975f5bc1`, with attribution and notices
preserved. The bounded extraction excludes aggregate classification fields
referenced to third-party sources. This archival finding does not activate WPP
or establish denominator fitness.

WHO's official dataset terms grant public-health-purpose rights to use,
reproduce, extract, download, copy and distribute covered datasets. They exclude
credited third-party material, require WHO and underlying-country attribution,
restrict non-minimal modification without written authorization and require a
withdrawal capability. The exact GHE workbook has no embedded file-level
licence or field-level third-party credit register. The owner-authorized exact,
unmodified copy is now preserved in the private Hugging Face archive at commit
`2f1014860cda849d86c895f722ef18c8d96b359b`; public redistribution,
non-minimal modification and derived-field activation remain withheld. Full
evidence and fail-closed rules are in
`docs/track-002-wpp-who-terms-audit-2026-08-15.yml`.

External scientific and data-governance dispositions remain pending for both
sources, and neither terms observation authorizes production activation.

### Repository-owned frontier reconciliation — 2026-08-15

The exact bounded source observations, candidate file selection and private
archive dispositions are now reconciled across the activation matrix and
Track 002 plan. Orphadata and WPP raw bytes are recorded as privately archived
under their observed Creative Commons terms but excluded from the bounded
candidate. WHO is privately preserved under its unmodified-copy and withdrawal
conditions; the bounded World Bank response is retained as probe-only. MONDO
`v2026-08-04` is pinned and all three canonical artifacts were verified against
publisher digests and privately archived at commit
`d5fcd47d39efe9cda57428caf0bcb4cc15c8c991`. Every estimand row remains
non-active.

The remaining unchecked work is not source discovery or repository control
implementation: it requires qualifying scientific and custodian receipts, a
real changed/unavailable-source exercise where such a condition is observed,
Track 007 gate satisfaction and an exact-candidate release decision. This
reconciliation does not satisfy or waive any of those gates.

### Aggressive lawful archive decision matrix — 2026-08-15

`docs/source-archive-decision-matrix-2026-08-15.yml` now assigns each current
and planned source to a public-raw candidate, private-raw, metadata/hash-only,
derived-only or controlled-environment-only route. GitHub remains the canonical
code, governance and manifest surface; the private Hugging Face repository is
the raw preservation surface; and the public dataset-estate registry contains
metadata only. No raw public mirror was created by this work.

The matrix makes the critical boundary explicit: permissively licensed files
may be packaged for a later exact public release decision, ambiguous or
third-party-bearing files remain private or metadata-only, and controlled
All of Us or Genomics England Research Environment data must never be exported
to either GitHub or Hugging Face.

The archive now additionally contains the exact ClinVar 2026-08 monthly
`variant_summary` snapshot, seven digest-verified HPO `v2026-06-23` core
artifacts, and a complete five-page PanelApp listing with 433 panel/version
rows. ClinVar remains non-diagnostic; HPO remains private until its embedded
terms route yields an exact accessible record; and PanelApp remains private,
non-commercial and non-diagnostic under its mixed third-party terms. The
PanelApp listing is complete, but the per-version detail capture is explicitly
incomplete after HTTP 429 (129 of 433 observed) and is not represented as a
complete snapshot.

### Private archive capacity stop — 2026-08-16

Historical UTS run `31897934633` did not create a remotely verified payload or
receipt: the Hugging Face LFS batch endpoint returned HTTP 403 with an explicit
private repository storage-limit message. The repository now records that
state as blocked and checks it before authentication, remote cursor planning or
UTS source download. A blocked invocation emits a redacted failure receipt and
cannot advance a cursor or authorize a redownload.

This is a repository-owned safety fix, not evidence that capacity has been
restored. Resumption remains blocked until a dated, expiring authenticated
capacity verification is reviewed and a one-artifact canary succeeds.

### PanelApp/OECD authoritative rights frontier — 2026-08-16

The response-hashed matrix in
`docs/track-002-panelapp-oecd-terms-matrix-2026-08-16.json` separates public
access mechanics, automation policy, content reuse and redistribution. The UK
publisher documents an operator-triggered panel-page TSV route for current and
selected prior versions, so this is the only permitted continuation while its
current robots policy disallows `/api/`. It is not a bulk-completeness route.
PanelApp Australia exposes public download controls and an API but also warns
of automated-client restrictions; no exact content licence was found, so its
raw/detail route remains metadata/hash-only.

OECD Health Statistics 2026 and dataflow
`OECD.ELS.HD/DSD_HEALTH_STAT@DF_COM/1.0` are now exact dataset identities. OECD
general terms permit reuse of OECD-owned data with attribution, but explicitly
require series-level inspection for source ownership and additional
restrictions. The public metadata index does not clear every series, so values
remain disabled until selected source tabs are recorded. Tests enforce these
fail-closed routes and prohibit treating public availability or an open-source
software licence as a content-redistribution grant.

### Bounded ClinVar metadata queue — 2026-08-16

The committed recursive observation now validates 56 sequential official
directory observations containing 6,410 directory, product, data or checksum
routes. The exact seven-seed, depth-two queue is exhausted and its inventory
fingerprint is verified before commit. The validator rejects unsafe hosts,
duplicate observation URLs, retained content, byte-route drift, claim upgrades,
fingerprint drift and inconsistent exhaustion state.

This closes only that fixed metadata queue. It does not establish product,
historical or global completeness, clinical validity, submitter authority or
redistribution rights. No source bytes, bodies, abstracts or full text were
retrieved or retained. Adding seeds, increasing traversal depth or activating a
product byte route requires a new bounded protocol and product-specific rights
evidence.

### BfArM German SNOMED CT metadata frontier — 2026-08-16

Official BfArM evidence now identifies the National Edition Germany as an RF2
bundle of the International Edition and German National Extension, released on
a semiannual schedule through authenticated MLDS. The repository records three
bounded publication events and explicitly rejects treating them as exact
package identities or complete history. It also preserves BfArM's warning that
the use-case-based German translation is not quality-assured and complete.

The UTS inventory contains 233 observed artifacts across six International,
Spanish, US, subset and mapping families but no German-labelled family. The
German extension is therefore an unresolved native-edition gap; its bundled
International content still requires exact-hash deduplication. Tests require
metadata-only public routing and prohibit private bytes until exact agreement,
territory and cloud-storage permission are all affirmative. No raw bytes were
downloaded or uploaded, and no licence, completeness or activation claim was
upgraded.

### MedLexSp and KIOM evidence frontier — 2026-08-16

The exact Digital CSIC observation identifies handle `10261/270429` as MedLexSp,
not an ontology, and binds the sizes and SHA-256 digests of its three public
documentation bitstreams. No lexicon payload was observed. The signed licence
requires confidentiality and prohibits third-party access, so public and
private-cloud byte routes remain disabled absent an express cloud/processor
grant; metadata, citation and hashes remain available.

The KIOM artifact retains authoritative publication provenance through DOI
`10.1093/bioinformatics/btq424`, but its named host failed DNS resolution. No
version, language inventory, bytes, checksum or redistribution licence is
inferred. The identity map also prevents treating TARA, OCMR or TCDO as copies
of KIOM merely because they concern traditional medicine. Five negative tests
enforce these boundaries; this closes evidence preparation only, not payload
acquisition, rights clearance, completeness or production activation.
