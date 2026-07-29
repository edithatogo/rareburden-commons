# Licence and acquisition policy

RareBurden Commons separates metadata review, access testing, licence review and
scientific approval. A source appearing in the catalogue does not authorise its
acquisition, redistribution or use in an analysis.

## Licence states

| State | Meaning | Automated acquisition |
|---|---|---|
| `verified` | Current terms were reviewed for the intended acquisition and use. | Permitted when the HTTPS evidence reference and all other acquisition controls are present. |
| `conditional` | Acquisition is permitted subject to recorded conditions. | Permitted only when the HTTPS reference records those conditions; downstream use must enforce them. |
| `unknown` | Rights or applicable terms have not been established. | Prohibited. Record a substantive rationale and use no source bytes. |
| `restricted` | Terms require a controlled, manual or otherwise restricted route. | Prohibited. Use manual registration only after authorised review. |
| `not_applicable` | The artefact is internally created or otherwise has no third-party data licence. | Permitted when this classification is accurate and documented. |

`verified`, `conditional` and `restricted` records require a persistent,
credential-free HTTPS terms or licence reference. Credentials, access tokens and
private query parameters must never appear in licence evidence.

## Fail-closed operator procedure

1. Identify the exact source release and intended use.
2. Review the current asset-specific terms; do not rely solely on a catalogue summary.
3. Record the licence state, dated evidence reference, conditions and reviewer role.
4. Use `fetch-release` only for `verified`, `conditional` or genuinely
   `not_applicable` artefacts. The command rejects `unknown` and `restricted`
   states before network access.
5. Use `register-release` for an authorised local file when automation is prohibited.
6. Treat a checksum mismatch as a source-change incident. Preserve the old manifest,
   do not overwrite the pinned release, and repeat licence and scientific review
   before registering new bytes.

For automated runs, pass `--source-change-report <path>` to `fetch-release`.
When observed bytes differ from the pinned SHA-256, no source file or acquisition
manifest is committed; a schema-valid `review_required` incident record is written
with redacted URL evidence, the expected and observed digests, and the required
review action.

This policy does not itself constitute legal, custodian, scientific or
data-governance approval.

## Approved-scope staging rule

Track 002 has an owner-approved candidate scope, but its exact releases are
still being pinned. Until the source-specific evidence is complete, operators
must use `world-bank-url` only to produce a reviewable query (with explicit
`--country`, `--year-start` and `--year-end`) and must not call `fetch-release`
for the candidate sources. This preserves the distinction between an approved
scope and an activated acquisition contract.
