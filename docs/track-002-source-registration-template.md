# Track 002 exact-source registration template

Use one completed record per production source candidate. This template is
deliberately non-binding: completing it does not activate acquisition or imply
scientific, data-governance or redistribution approval.

## Required record

```yaml
source_id: ""
publisher: ""
title: ""
exact_url: ""
landing_page_url: ""
release_or_version: ""
retrieved_at_utc: ""
mime_type: ""
size_bytes: null
sha256: ""
licence_or_terms_url: ""
licence_state: "unknown"
attribution_text: ""
redistribution_position: "unknown"
third_party_material: "unknown"
intended_use: ""
geography_scope: ""
time_scope: ""
measure_unit: ""
scientific_reviewer: "pending"
data_governance_reviewer: "pending"
decision: "pending"
decision_record_url: ""
```

## Completion rules

- `exact_url`, release/version, retrieval time, MIME, byte count and SHA-256
  must describe the same bytes.
- `licence_state` may be `unknown` only while the record is a candidate; an
  unknown or restricted state must fail closed for automated acquisition.
- `redistribution_position` must distinguish public metadata, cached source
  bytes, derived aggregates and prohibited redistribution.
- Scientific and data-governance reviewers must decide against the exact
  record, not merely the publisher landing page.
- Do not commit downloaded UN/WHO bulk bytes, credentials or controlled data.

## Current unresolved records

The open candidates are the UN WPP 2024 workbook and one WHO Global Health
Estimates aggregate file. Their landing pages and methodology/terms evidence
are recorded in the Track 002 review, but stable exact file routes and
hash-bound decisions are not yet recorded. Until this template is completed,
the corresponding adapters remain synthetic/registration-only.

## Safe fallback

If a publisher exposes no stable downloadable route, attach a manual
registration receipt containing the page URL, filename, retrieval timestamp,
publisher-provided checksum (if any), terms snapshot and a bounded
non-redistribution cache policy. A missing checksum or unclear rights remains a
blocking finding; do not guess a URL or silently substitute another release.
