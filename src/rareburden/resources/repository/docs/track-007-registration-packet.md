# Track 007 registration and screening packet

**Protocol:** `RBC-LAND-007 v0.2.0`
**Status:** frozen and hash-registered in the repository; no external registry
event is claimed

**Owner:** Programme and Evidence Synthesis Leads
**Scope:** public rare-disease burden, registry, ontology, genomic, policy,
standards and methods infrastructure relevant to a provenance-first burden
layer.

## Repository registration

The canonical protocol is `docs/track-007-protocol-v0.2.0.md`. Its SHA-256,
Git blob identifier and bound evidence set are recorded in
`docs/track-007-repository-registration-2026-08-16.yml`. This content-addressed
repository registration is the normative Track 007 snapshot. External registry
submission is optional supplementary evidence; OSF is deferred and removed
from the active plan.

## Search-log schema

Record one row per query execution. Raw exports remain outside public Git when
they contain provider identifiers or terms that prohibit redistribution; commit
only lawful metadata, hashes and bounded first-page identifiers.

| Field | Required value |
|---|---|
| protocol_version | `RBC-LAND-007 v0.2.0` |
| registry | Zenodo, GitHub, Hugging Face, scholarly or institutional source |
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

## Required advisory challenges and decision

- Role-separated methods agents recommend accept, narrow, revise, defer or stop
  after challenging the question, strings, eligibility, deduplication,
  exclusions and coverage limits.
- Role-separated community/harm agents challenge relevance, harms, language,
  equity and acceptable interpretation. Their advice is not patient/community
  consent or constituted-community approval.
- The repository owner records the attributable disposition and claim boundary.

Until the agent challenges and owner disposition are bound to the exact
repository registration, `proceed_with_narrowed_scope` remains provisional and
Track 007 stays in review. No additional-person or independent review gate
applies under ADR-0009.
