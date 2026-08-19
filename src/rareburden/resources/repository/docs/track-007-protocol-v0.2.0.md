# Track 007 landscape protocol v0.2.0

**Purpose:** Freeze the repository-native protocol for the bounded RareBurden
Commons landscape and adjacency review.

**Status:** Frozen repository protocol; not externally registered and not a
claim of systematic, comprehensive or globally representative coverage.

**Protocol identifier:** `RBC-LAND-007`

**Version:** `0.2.0`

**Frozen on:** 2026-08-16

## Review question

Which publicly identifiable rare-disease burden, registry, ontology, genomic,
policy, standards and methodological infrastructures overlap with or
complement a federated measurement, provenance and policy-translation layer,
and what evidence-bounded gap or boundary remains?

## Intended decision

The review supports one of `proceed`, `proceed_with_narrowed_scope`, `combine`,
`revise`, `defer` or `stop`. It does not establish partnership, endorsement,
data access, superiority, clinical validity or ownership of community
knowledge.

## Active discovery sources

The frozen public-web discovery surface is:

1. GitHub repository search API;
2. Zenodo records API;
3. Hugging Face datasets API;
4. Crossref works API as the scholarly metadata index; and
5. official institutional sources named in `catalog/initiatives.yml`.

OSF is deferred by owner decision and is not part of the active search surface.
Its historical endpoint observations are retained only as historical evidence.
External protocol registration is optional supplementary evidence and is not a
condition for reconstructing this repository snapshot.

## Frozen query families

Each active public API is queried separately with these exact UTF-8 strings:

1. `rare disease burden`
2. `rare disease registry`
3. `rare disease ontology`
4. `rare disease prevalence`
5. `rare disease cost`

Official institutional sources are searched using the initiative name,
documented alternate name and official domain. A query change creates a new
protocol version; it does not rewrite this snapshot.

## Retrieval and preservation

For every request, preserve the source, exact request URL, final URL, UTC
retrieval window, HTTP outcome, provider total or cap when reported, response
SHA-256, bounded result identifiers and stop reason. Public metadata may be
retained when lawful. Abstracts, repository bodies, dataset cards and
copyrighted full text are not retained by the bounded capture workflow.

Pagination is bounded by the versioned strategy in
`docs/track-007-pagination-strategy-2026-08-15.json`. Reaching an endpoint total
means only that the endpoint returned its retrieval-time total for that query.
An empty page, page-budget stop or provider cap is never interpreted as absence
or completeness.

## Eligibility

Include a record for adjacency assessment when it is publicly identifiable,
has a stable landing page or persistent identifier, and materially contributes
one or more of:

- a rare-disease burden or prevalence estimate;
- a registry, catalogue or data infrastructure;
- an ontology, nomenclature or interoperability standard;
- a policy or programme mandate relevant to measurement; or
- a method relevant to provenance, uncertainty, equity, governance or burden
  estimation.

Potential competitors, complements and foundational dependencies are eligible.

Exclude a record when the retained evidence establishes one of the closed
reasons: no rare-disease scope signal, purely clinical guidance without a
measurement or data contribution, individual case report, generic mention
only, inaccessible description with no assessable public metadata, exact
duplicate, superseded duplicate or this repository's own self-result. Failed
or access-restricted locators remain pending lawful assessment and are not
excluded automatically.

## Deduplication and screening

1. Assign a stable record identifier and retain the source identifier.
2. Normalise title, canonical URL or DOI, organisation and year without
   silently coercing missing values.
3. Remove exact identifier and canonical-URL duplicates while preserving a
   link to the retained record.
4. Flag entity and exact-title clusters for evidence-bound adjudication;
   matching names alone do not establish equivalence.
5. Screen retained title and public metadata as `include`, `exclude`,
   `uncertain` or `pending` with a closed reason vocabulary.
6. Require a lawful evidence SHA-256 for final content-level eligibility.
7. Preserve exclusions and count reconciliation; never delete inconvenient
   results.

Role-separated methods and community/harm agents challenge the protocol and
claims. Their findings are advisory. The repository owner records the
accountable disposition. Neither step is described as independent, human,
constituted-community, institutional or external review.

## Extraction fields

Extract: stable identifier; title; canonical URL or DOI; organisation; year;
source registry; record type; geography; disease scope; access class; purpose;
methods; outputs; maturity; RareBurden relationship; duplicate keys; screening
decision and reason; evidence hash; uncertainty; limitations; and claim-source
links.

## Count reconciliation

For each immutable capture, report occurrences discovered, exact duplicates,
unique records, screened records, included records, excluded records, uncertain
records and pending records. Counts are bound to a retrieval window, provider,
query family, page budget and protocol version. Provider totals are observations
and may drift.

## Bias, coverage and representativeness

The active indexes privilege public, indexable and predominantly English
metadata. Ranking, provider indexing, language, geography, time, grey
literature, inaccessible systems, missing metadata and page budgets create
known coverage limits. The captured results are a bounded adjacency sample,
not a census. Comprehensive coverage, global representativeness and novelty
confirmation remain prohibited claims.

## Challenge and decision rules

Methods agents challenge query fitness, source coverage, ranking, pagination,
deduplication, eligibility, count reconciliation, falsifiability and novelty
boundaries. Community/harm agents challenge terminology, accessibility,
regional and non-English erasure, equity, acceptable use, framing and risks of
implied endorsement or ownership.

Any critical methodological, harm, rights, semantic-integrity or
reproducibility finding requires `revise`, `narrow`, `defer` or `stop`. A
material change to sources, queries, eligibility, decision categories or claim
boundaries requires a new protocol version and hash set.

## Frozen evidence inputs

- `docs/track-007-search-log-2026-08-14.yml`
- `docs/track-007-search-results-2026-08-15.json`
- `docs/track-007-screening-2026-08-15.json`
- `docs/track-007-screening-resolutions-2026-08-15.json`
- `docs/track-007-fulltext-locator-observations-2026-08-15.json`
- `docs/track-007-fulltext-eligibility-2026-08-15.json`
- `docs/track-007-live-capture-coverage-2026-08-15.json`
- `docs/track-007-title-cluster-adjudication-2026-08-15.json`
- `catalog/initiatives.yml`

The repository registration manifest binds this protocol and each frozen input
by SHA-256 and Git object identifier.
