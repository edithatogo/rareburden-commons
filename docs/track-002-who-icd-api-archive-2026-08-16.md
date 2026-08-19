# WHO ICD API release inventory and archive boundary — 2026-08-16

## Outcome

The authenticated WHO ICD API v2 route is operational and now has a bounded,
rate-limited inventory workflow. The dated public manifest is
`manifests/classifications/who-icd-api-inventory-2026-08-16.json`.

The observation is metadata evidence, not a complete classification archive or
production activation. The workflow stores exact authenticated top-level JSON
responses only in the private `edithatogo/hpo-licensed-ontology-archive`
dataset, verifies the remote file sizes, and lets runner-local bytes expire.
Only endpoint, release, language, status, size and SHA-256 metadata are emitted
as the public Actions artifact and checked-in manifest.

## Observed API scope

The API documents and exposes:

- the WHO-FIC Foundation top level;
- ICD-11 MMS releases;
- ICF as an ICD-11 linearization where the requested release exists; and
- ICD-10 releases 2008, 2010, 2016 and 2019.

The 2026-01 Foundation endpoint advertises the union of languages available in
the API. Each MMS and ICF release is separately queried because release-level
language sets differ. A 404 for a historical ICF route is preserved as an
explicit unavailable observation rather than inferred as a release.

WHO's official API documentation states that API v2 requires the `API-Version:
v2` header, uses OAuth 2 client credentials, supports `Accept-Language`, and is
scoped to Foundation, ICD-11 linearizations and ICD-10:

- <https://icd.who.int/docs/icd-api/APIDoc-Version2/>
- <https://icd.who.int/docs/icd-api/ReleaseNotes-Version2.6/>
- <https://icd.who.int/icdapi/docs2/SupportedClassifications/>

## Fail-closed boundaries

- ICD-10 release responses do not expose `availableLanguages`; the inventory
  does not infer language completeness from an English response.
- ICHI, historical ICD revisions 1–9, WHO derived/related classifications and
  national ICD modifications require separate official routes and rights
  records.
- API response availability does not establish public redistribution rights.
- Raw observations remain private and are not committed to Git or uploaded to
  the public Hugging Face estate.
- No API observation activates an estimand, clinical use or production source.
- Authentication failures, unexpected response shapes, untrusted hosts,
  non-JSON payloads and unhandled HTTP statuses stop the workflow.

## Rate and secret controls

Requests are sequential with a two-second floor. HTTP 429 and transient gateway
errors use bounded `Retry-After`/exponential backoff. The client ID, client
secret, token URL and API base URL are GitHub Actions secrets; bearer tokens and
credentials are never included in receipts or logs.
