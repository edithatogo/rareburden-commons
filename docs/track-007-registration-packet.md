# Track 007 registration and screening packet

**Protocol:** `RBC-LAND-007 v0.1.0`  
**Status:** versioned draft; not externally registered  
**Owner:** Programme and Evidence Synthesis Leads  
**Scope:** public rare-disease burden, registry, ontology, genomic, policy,
standards and methods infrastructure relevant to a provenance-first burden
layer.

## Registration handoff

Submit the versioned protocol in `conductor/tracks/007-landscape-novelty/review.md`
and this packet to the chosen registration service. Preserve the submitted
snapshot, public identifier, submission timestamp and any requested amendments.
If registration is unavailable, publish the draft and logs locally but do not
call it registered.

## Search-log schema

Record one row per query execution. Raw exports remain outside public Git when
they contain provider identifiers or terms that prohibit redistribution; commit
only lawful metadata, hashes and bounded first-page identifiers.

| Field | Required value |
|---|---|
| protocol_version | `RBC-LAND-007 v0.1.0` |
| registry | GitHub, Zenodo, OSF, Hugging Face, scholarly or institutional source |
| query_string | exact submitted string, including field filters |
| endpoint_or_database | canonical URL or database name |
| retrieved_at_utc | ISO-8601 timestamp |
| http_status | numeric status or `not_applicable` |
| result_total | provider total, or `not_reported` |
| export_sha256 | hash of retained lawful export, or `not_retained` |
| first_page_ids | stable identifiers for the bounded inspected page |
| operator | role, not a credential or personal secret |
| notes | rate limits, ranking, pagination and known limitations |

## Screening and exclusions fields

Each discovered record receives a stable `record_id` and these fields:

`title`, `canonical_url_or_doi`, `organisation`, `year`, `source_registry`,
`record_type`, `rareburden_relevance`, `stable_identifier`,
`exact_duplicate_key`, `entity_duplicate_key`, `title_metadata_decision`,
`full_metadata_decision`, `decision_reason`, `reviewer`, `second_reviewer`,
`screened_at_utc`, `uncertainty_note`, `exclusion_reason`, `supersedes`, and
`claim_source_links`.

Allowed decisions are `include`, `exclude`, `uncertain`, and `awaiting_second_review`.
Excluded records are retained with a one-line reason; they are never deleted to
make counts look favourable. Entity-level duplicates must point to the retained
canonical record.

## Count reconciliation

Report discovery, exact deduplication, entity deduplication, screened, included,
excluded, uncertain and awaiting-second-review counts. Counts are tied to the
protocol version and retrieval window; changed API totals require a new search
log row, not an overwrite.

## Required external decisions

- Methods reviewer: accept, revise or reject the question, strings, eligibility,
  deduplication and exclusion rules.
- Patient/community reviewer: assess relevance, harms, language, equity and
  acceptable interpretation.
- Programme/release decision: allow only bounded adjacency and gap claims;
  prohibit partnership, endorsement or data-access claims without evidence.

Until these records exist, `proceed_with_narrowed_scope` remains provisional and
Track 007 stays in review.
