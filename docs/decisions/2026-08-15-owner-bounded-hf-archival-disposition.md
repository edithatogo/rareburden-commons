# Owner bounded Hugging Face archival disposition — 2026-08-15

## Decision

The repository owner approves raw archival of each Orphadata file only after its
exact file-level licence and attribution are recorded. Files without that
confirmation remain metadata/hash-only.

WPP and WHO workbook bytes remain private-local or absent from Hugging Face until
exact redistribution terms, third-party restrictions and attribution requirements
are documented. Metadata, hashes and lawful derived outputs may be archived.

The exact candidate scope is synthetic fixtures plus verified public source
observations with recorded release identity, SHA-256, terms and intended metric
use. All other sources remain disabled or metadata-only.

The bounded synthetic/public-preview disposition runs through 2026-09-03. Any
material source, rights, semantic, security, reproducibility or scope change
requires a new decision. Critical failures require stop or withdrawal.

## Authority boundary

This is an owner decision for repository preparation and bounded preview. It is
not independent scientific, patient/community, custodian, security, operator,
backup-owner or release-authority evidence. Production activation and stable
release remain disabled.

## Current source posture

| Source | Raw Hugging Face archival | Activation |
|---|---|---|
| Orphadata | Conditional on exact file-level licence and attribution | Disabled pending disposition |
| WPP | Archived at exact hash after the workbook's embedded CC BY 3.0 IGO notice and third-party classification boundary were documented | Disabled |
| WHO GHE | No bytes until workbook and credited material terms are documented | Disabled |
| World Bank | Query/hash metadata only | Probe-only |

## Subsequent exact-workbook evidence

The exact WPP workbook audit in
`docs/track-002-wpp-who-terms-audit-2026-08-15.yml` recorded its embedded CC BY
3.0 IGO notice, citation and third-party classification references. The exact
unmodified workbook was then archived privately at Hugging Face revision
`ae188ced2bced5e403e82af61990a28f975f5bc1`. This satisfies the bounded raw
archival condition only; activation and denominator fitness remain separately
disabled.

WHO's publisher terms permit an unmodified private copy for public-health use,
subject to attribution and withdrawal, but the exact workbook contains no
file-level licence or field-level third-party credit register. Its Hugging Face
raw upload therefore remains withheld and redistribution remains conditional.
