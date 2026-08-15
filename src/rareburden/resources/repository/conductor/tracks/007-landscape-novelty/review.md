# Track 007 internal review — Landscape, adjacency and novelty

**Review date:** 2026-07-27; current closeout review 2026-08-16

**Current decision:** In review. The protocol is repository hash-registered.
Role-separated agent challenge and repository-owner disposition remain pending.
External registry submission is optional, and OSF is deferred.

## Current closeout evidence — 2026-08-16

`docs/track-007-protocol-v0.2.0.md` freezes the review question, active search
surface, five query families, eligibility, deduplication, count reconciliation,
coverage limits, challenge rules and stop triggers. The content-addressed
registration in `docs/track-007-repository-registration-2026-08-16.yml` binds
the protocol and its evidence inputs by SHA-256 and Git blob identifier.

`docs/track-007-bounded-evidence-synthesis-2026-08-16.md` reconciles the frozen
first-page screen, locator workflow and separate live pagination exercise. It
keeps all content-level decisions, broader coverage, representativeness and
novelty claims fail-closed. `docs/track-007-agent-challenge-task-2026-08-16.yml`
defines the exact input hashes, role remits, required findings and assurance
boundary for the remaining advisory challenge.

The dated sections below preserve the historical evidence state at the time
they were written. Their former external or additional-person gate wording is
superseded prospectively by ADR-0009; historical observations are not rewritten.

### Methods and coverage challenge — 2026-08-16

The role-separated methods and coverage challenger verified every input hash
and Git blob binding, then recommended **narrow**. The full advisory findings
are recorded in `docs/track-007-agent-panel-findings-2026-08-16.yml`.

Three High findings remain: all 69 retained records lack final content-level
eligibility decisions; the separate 306-occurrence live capture is unscreened
and unreconciled; and scholarly coverage is limited to ranked Crossref first
pages without executable pagination or database-specific bibliographic
searches. Medium findings limit deduplication to the frozen snapshot, identify
English and ranking bias, distinguish capture-mechanics reproducibility from
exact response reproduction, and require institutional records to be labelled
as curated seeds.

The exact `133 occurrences -> 120 unique -> 69 retained / 51 excluded` snapshot
counts remain valid. They do not satisfy the original broad landscape scope.
The community/harm challenger also recommended **narrow and revise framing**.
Every gap or niche statement must be bounded to the indexed English-language
public evidence sampled; the 13 catalogue records are owner-curated examples,
not a global inventory; inaccessible evidence is `not_assessable`, not absent
or irrelevant; and no patient/community legitimacy or approval exists. Public
framing must state that burden measurement does not value lives, rank
conditions or justify rationing, and must preserve lived-impact, equity and
accessibility limitations.

The governance/rights/reproducibility and additional
scientific/search-reproducibility challenges confirmed the narrow direction and
required provider-terms, exact-candidate, retrospective-protocol, correction
and withdrawal controls. Those repository remediations are recorded in:

- `docs/track-007-provider-terms-matrix-2026-08-16.yml`;
- `docs/track-007-correction-withdrawal-map-2026-08-16.yml`;
- `docs/track-007-bounded-framing-addendum-2026-08-16.md`; and
- `docs/track-007-owner-disposition-ready-2026-08-16.yml`.

All challenge roles are complete and the panel consensus is **narrow and
remediate**. The exact-candidate repository-owner disposition remains pending,
so the track stays **In review** and the original publication-ready landscape
acceptance is not claimed.

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

### Bounded pagination implementation — 2026-08-15

Repository review result: **Pass for capture mechanics; broader gates remain
open**. The pagination workflow records every request/final URL, response hash,
item count and stable identifier, enforces a bounded page budget, rejects
changing totals and repeated cross-page identifiers, and distinguishes provider
totals/caps from observed page exhaustion. Deterministic fixtures exercise exact
total capture, page-budget exhaustion, unstable totals, duplicate pages, invalid
JSON and HTTP failure. This supports reproducibility of captured public pages;
it does not establish search, ecosystem, scholarly, language or temporal
completeness. Live multi-page capture, full-text eligibility, external protocol
registration, independent methods challenge and patient/community
interpretation remain open.

### External-gate panel synthesis — 2026-08-01

The repository's preparatory panel review is recorded in
`docs/v1-subagent-panel-report-017.md` and governed by
`docs/decisions/ADR-0007-external-gate-handling.md`. It supports continued
bounded public/synthetic preparation, while confirming that protocol
registration, broader screening, independent methods review and
patient/community challenge remain open. The panel is not an external review
body and this note does not change the track's `in_review` status.

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

### Registration packet refresh — 2026-08-01

`docs/track-007-registration-packet.md` now provides the versioned registration
handoff, search-log schema, screening/exclusion fields, count reconciliation and
reviewer decisions. It is repository-owned preparation only: no external
protocol identifier, independent methods review or patient/community decision
is inferred.

The 2026-08-01 discovery observations are also preserved in
`docs/track-007-search-log-2026-08-01.yml`; each row is explicitly marked
discovery-only/unscreened (or exact-title-only for OSF).

### Five-query discovery refresh — 2026-08-14 UTC

The five protocol query families were rerun against GitHub, Zenodo and Hugging
Face dataset APIs, with Crossref added as a reproducible scholarly metadata
index. `docs/track-007-search-log-2026-08-14.yml` records exact retrieval
timestamps, provider totals (where reported), response hashes and bounded
first-page identifiers; `scripts/refresh_track_007_searches.py` makes the
request construction and metadata extraction repeatable. OSF was not queried
because its active route is deferred by owner decision.

The broad Zenodo and Crossref totals demonstrate retrieval and ranking behavior,
not eligibility or coverage. The complete bounded first pages were subsequently
preserved and title/public-metadata screened in
`docs/track-007-search-results-2026-08-15.json` and
`docs/track-007-screening-2026-08-15.json`. Across 133 returned occurrences, 13
exact cross-query/DOI duplicates were removed and all 120 unique records were
screened: 69 were retained for adjacency/full-text review, 51 were excluded,
and none remain uncertain after the sole missing-title DOI was resolved through
hashed Crossref metadata as a grant without a rare-disease scope signal. Four exact-title
clusters were flagged rather than automatically entity-merged. These counts do
not alter the provisional novelty claim or external-gate status. Pagination,
full-text eligibility, coverage, registration, independent methods challenge
and accountable patient/community interpretation remain pending.

The resolution is bounded to the committed first-page snapshot. Pagination,
full-text eligibility, entity-level adjudication, coverage and final novelty
remain repository-owned or external work as identified above; zero uncertainty
in this snapshot is not a completeness claim.

The pagination capture workflow now emits a v0.2 record containing only each
result's stable identifier, title and canonical URL in addition to page hashes.
This closes the metadata-contract gap for future immutable captures while
deliberately excluding abstracts, repository bodies, dataset cards and full
text. The change does not retrofit or reinterpret earlier evidence and does not
establish eligibility, coverage, representativeness or novelty.

The refreshed files are hash-bound in
`docs/track-007-registration-challenge-readiness-2026-08-15.yml`. The challenge
packet adds explicit questions about low-specificity scholarly/repository
results, ranking and pagination, cross-index deduplication, public-web and
language bias, and exclusion of this repository as a self-result. It remains
preparation evidence and cannot satisfy the external receipts it requests.

### Synthetic screening exercise — 2026-08-02

The deterministic fixture `docs/track-007-panel-screening-exercise-2026-08-02.yml`
and its regression test exercise the count reconciliation rule and preserve an
uncertain record without treating it as included. This is repository-owned
panel preparation evidence only. External protocol registration, independent
methods challenge and patient/community challenge remain open; no novelty,
completeness, partnership or endorsement claim is upgraded by this exercise.

### Bounded full-text eligibility workflow — 2026-08-15

The 69 records retained at title/public-metadata screening now have a complete,
deterministic locator register and fail-closed eligibility state machine. A
HEAD-only audit retained HTTP status, final URL and content type but no response
body, abstract or copyrighted full text. At the recorded observation time, 61
locators were reachable and 8 were access-restricted. Reachable records remain
`pending_content_assessment`; restricted records remain
`pending_lawful_access`. A failed or restricted locator is never automatically
excluded.

Final include/exclude/uncertain resolutions require an evidence SHA-256 and use
a closed exclusion-reason vocabulary. Schema and negative tests reject missing
observations, URL substitution, unsupported exclusion reasons, unbound
resolutions and any locator observation containing abstract or full-text
fields. This completes repository-owned workflow construction and locator
observation only. Final eligibility, pagination/completeness, novelty,
registration, independent methods challenge and accountable patient/community
interpretation remain pending.

### Bounded live pagination and coverage disposition — 2026-08-15

The five frozen queries were exercised against GitHub, Zenodo and Hugging Face
with a two-page, 25-record budget. GitHub reached its retrieval-time endpoint
totals for all five queries (56 occurrences). Zenodo captured 250 occurrences
but hit the page budget for every query against much larger provider totals.
Hugging Face returned empty first pages, which is recorded only as endpoint
behavior and not as evidence that matching datasets do not exist.

Every provider file records exact URLs, timestamps, response hashes, identifiers
and stop reasons and is hash-bound by
`docs/track-007-live-capture-coverage-2026-08-15.json`. The coverage disposition
keeps scholarly, grey-literature, language, geography, temporal and restricted
material coverage incomplete or unmeasured. Comprehensive coverage, global
representativeness and upgraded novelty claims remain prohibited. Newly captured
record screening and the external challenge gates remain open.

### Exact-title cluster adjudication — 2026-08-15

All four title clusters flagged by bounded screening now have record-level rules
backed by exact GitHub or Crossref response hashes. Reciprocal Crossref relations
link the Dercum's disease preprint and journal article as versions of one work
without deleting either record. The three GitHub pairs have distinct immutable
repository/node identifiers and no declared fork, parent or source relation, so
they remain separate repository records.

This does not establish that the GitHub pairs are distinct initiatives. Their
initiative-level equivalence remains unresolved because shared names or
descriptions are insufficient evidence. The adjudication removes silent
record-level merging risk without narrowing external challenge requirements.
