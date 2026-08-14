# Track 008 semantic review packet

**Status:** non-binding preparation; Track 008 remains blocked  
**Contract draft:** semantic contract v0.1.0  
**Activation rule:** no v0.4 contract freeze or source-pinned semantic release
until Tracks 002 and 007 pass their gates.

## Decisions required

| Decision | Evidence to inspect | Accountable disposition |
|---|---|---|
| Source releases and licence states | Exact source-release records, hashes and terms from Track 002 | approve, revise, bounded or reject |
| Stable identifiers and relation meanings | Mapping schema, loader, version diff and provenance fields | approve or revise |
| Ambiguous/one-to-many handling | Fail-closed aggregation tests and unresolved mapping examples | approve or revise |
| Burden-purpose hierarchy | Synthetic golden fixtures, conservation and overlap reports | approve, narrow or reject |
| Naming/grouping harms | Patient/community review of labels, syndromes, aetiologies and categories | approve, revise or dissent |
| Deprecation/migration | Version-diff fingerprints and affected-output invalidation rules | approve or revise |

## Repository evidence

- `schemas/ontology-mapping.schema.json` and related semantic schemas define
  explicit relation, confidence, provenance and validity fields.
- `src/rareburden/semantics.py` and mapping diff tooling preserve ambiguity and
  produce deterministic release-impact information.
- Synthetic golden fixtures cover monogenic diabetes, bronchiectasis and
  paediatric examples; they are not clinical evidence.
- Track 002 and Track 007 review records remain the upstream gate references.
- `docs/track-008-source-release-inventory-2026-08-03.yml` records candidate
  sources, unresolved release/checksum/terms fields and fail-closed activation.
- `docs/track-008-semantic-challenge-panel-2026-08-03.yml` defines the
  panel-assurance challenge, quorum, questions, dissent and stop triggers; it
  is not an external authority receipt.
- `docs/track-008-naming-harm-review-packet-2026-08-03.yml` defines the
  bounded label, grouping, accessibility and harm questions for panel advice;
  contested terminology remains fail-closed.
- `docs/track-008-panel-assurance-report-2026-08-03.yml` records the three-role
  panel findings, conservative remediation and bounded recommendation.

## Required release packet before activation

The eventual semantic release must include a machine-readable mapping set,
human-readable report, source release IDs/hashes, licence states, migration and
deprecation notes, unresolved mapping list, overlap/conservation report,
software/environment identity and the semantic/clinical, patient/community and
engineering dispositions. Unknown or ambiguous mappings remain visible and fail
closed where aggregation would double count.

## Unsupported mappings and residual overlap boundary

Mappings with `unmapped`, `ambiguous`, `deprecated`, or unsupported relation
states remain visible in the source mapping set and are never silently promoted
to an aggregate. Multi-aetiology and multi-diagnosis relationships are
explicitly non-exclusive unless a conservation contract proves otherwise;
residual overlap is reported as unresolved rather than removed by selection.

## Safe continuation

Continue synthetic schema, migration and impact tests. Do not pin a production
ontology release, publish a clinical naming claim, or freeze a v0.4 contract
until the required reviewers and upstream evidence are present.
