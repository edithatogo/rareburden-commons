# Track 002 public history and product discovery

This receipt records a credential-free, bounded observation of four official
publisher surfaces on 2026-08-16. The deterministic manifest is
`manifests/classifications/public-history-products-2026-08-16.json` with
inventory SHA-256
`e1dbb3675c80f1c43e9cd3d9e0cf203e6bcb9cdbe5e11332336eb166ce44a88e`.

| Family | Enumerated records | Exact bounded surface | Byte route |
|---|---:|---|---|
| ORPHAcode | 71 | current official nomenclature-pack page | reuse the existing public archive by digest; CC BY 4.0 |
| Orphadata | 94 | eight current scientific product pages | reuse the existing public archive by digest; CC BY 4.0 |
| MONDO | 100 | first 100 releases returned by the official GitHub Releases API | CC BY 4.0 assets are eligible only after exact digest comparison |
| ClinVar | 80 | current official NCBI tab-delimited archive index | metadata only pending product- and submitter-provenance disposition |

The two Orphanet inventories reproduce the counts already bound by the
Hugging Face receipts. They therefore authorize no upload: an equivalent hash
must reuse the existing path and receipt. MONDO identifies historical release
and asset routes, but this slice does not fetch those potentially large assets.
ClinVar records official archive links without inferring that public download
availability grants unrestricted redistribution of contributor assertions.

The observer is sequential, waits at least one second between live publisher
requests and rejects any metadata response over 8 MB. It strips URL fragments,
accepts only exact official hosts and known file suffixes, and emits no source
payload bytes. The GitHub Actions workflow regenerates an ephemeral metadata
artifact; committed observations change only through a reviewed update.

## Deliberate limits

- The MONDO API observation is one page of 100 releases, not all releases.
- Current ORPHAcode and Orphadata pages do not prove historical, withdrawn or
  unavailable language coverage.
- The ClinVar index does not establish product completeness, submitter rights,
  clinical validity or suitability for diagnosis.
- No inventory establishes all-version, all-language or product completeness.
- No existing Hugging Face object was deleted or duplicated by this slice.

Next safe increments are cursor-based MONDO pagination with digest-first byte
routing, official Orphanet change-file discovery if such a surface becomes
available, and ClinVar product-specific metadata inventories. Each increment
must retain fixed page/byte/request budgets and the same fail-closed rights
rules.
