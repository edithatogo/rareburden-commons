# Track 002 credential-free public history frontier

The deterministic frontier manifest
`manifests/classifications/public-history-frontier-2026-08-16.json` records an
official-source observation with SHA-256
`d6f9317203cd0cd7aa352e429fd0467e7758e328084f72c7e0237d86cb89e8d6`.

| Family | Pages | Records | Exhaustion evidence | Routing |
|---|---:|---:|---|---|
| MONDO releases | 2 | 120 releases | second page contained fewer than 100 records | release metadata public; CC BY 4.0 assets require digest-first deduplication |
| ClinVar | 7 | 134 product, directory, data or checksum links | fixed official directory set only | metadata-only pending product and submitter-provenance review |
| Orphadata WordPress media | 2 | 125 media records | second page contained fewer than 100 records | metadata-only; exact file terms not inferred |
| ORPHAcode WordPress media | 1 | 92 media records | first page contained fewer than 100 records | metadata-only; exact file terms not inferred |

The MONDO GitHub Releases API was enumerated until its observed empty frontier
under a ten-page ceiling. This closes pagination for that exact API response at
the retrieval event, not every MONDO artifact, tag, branch or future release.
Historical bytes remain unmaterialized until each asset digest is compared
with the current public and private archive receipts.

ClinVar observations cover the FTP root, tab-delimited archive, XML archive,
GRCh37 and GRCh38 VCF 2.0 archives, document archives and release notes. The
index parser retains product directories plus data and checksum routes, but
does not recurse into every child directory. Public availability is not
treated as blanket redistribution permission for submitter assertions.

Both official Orphanet WordPress media APIs were paginated to their observed
frontiers. The 217 records were images (PNG or JPEG); no historical data pack,
withdrawal ledger, language release index or machine-readable change file was
exposed by these media APIs. This is a bounded negative observation, not proof
that those resources do not exist elsewhere.

All requests were sequential with at least a one-second delay and an 8 MB
response ceiling. URLs require exact HTTPS hosts and path-prefix containment.
Cross-host and path-escape links fail closed. Equivalent bytes must reuse an
existing digest/path/receipt; this slice downloaded no source payload bytes and
created no duplicate Hugging Face objects.

## Remaining safe frontier

- compute and compare exact MONDO asset digests before any historical upload;
- recurse into selected ClinVar product-year directories under separate fixed
  request and record budgets, retaining metadata-only rights posture;
- observe a publisher-linked Orphanet history or change surface if one becomes
  discoverable, without guessing URL patterns or treating current pages as a
  historical catalogue;
- repeat the inventory as a new dated receipt rather than rewriting this one.
