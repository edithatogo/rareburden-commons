# Track 002 MONDO materialization and ClinVar metadata frontier

## MONDO materialization contract

The observed 120-release MONDO frontier contains 1,916 release assets with
publisher-declared bytes totalling 128,438,860,575 (about 128.4 GB). The exact
frontier is bound by
`manifests/classifications/public-history-frontier-2026-08-16.json`.

`.github/workflows/archive-mondo-release-batch.yml` therefore processes one
explicit release/asset cursor at a time. Each run:

- accepts only exact `github.com` HTTPS asset URLs from the pinned manifest;
- caps selected and streamed bytes at 500 MB;
- waits two seconds between assets;
- computes SHA-256 while streaming to ephemeral runner storage;
- uses `raw/mondo/<release>/<filename>` in the existing public archive;
- reuses an existing object only when size and remote LFS SHA-256 both match;
- fails on path, size or digest conflict;
- verifies the remote object after upload, emits a receipt and deletes the
  runner copy.

MONDO's repository release assets are routed under CC BY 4.0. The workflow is
incremental because the full frontier is too large for one safe job. A green
canary proves only the exact selected asset receipt, not that 1,916 assets or
120 releases have been archived. The existing three v2026-08-04 files retain
their earlier paths and receipts and are never duplicated when their digests
match.

## ClinVar recursive metadata receipt

`manifests/classifications/clinvar-recursive-metadata-2026-08-16.json` has
inventory SHA-256
`160450482c80fd8756c78aa51e3eebda38e92960c61f956f024f1dc1330250d4`.
It records 56 sequential official directory observations and 6,410 contained
directory, product, data or checksum routes at depth no greater than two. The
queue is exhausted within this exact seven-seed, depth-two scope only.

The root index is observed but is not recursively followed into temporary or
unselected products. Recursion is restricted to the seven named product/archive
seeds, exact `ftp.ncbi.nlm.nih.gov` HTTPS URLs and path-prefix containment.
HTTP 403/404 and exhausted transient retries are recorded as unavailable and
never bypassed. No ClinVar product bytes are fetched; every route remains
metadata-only until product-specific rights and submitter provenance are
bound.

## Remaining work

Hosted run `31900342354` archived and remotely verified asset indices 1-2 for
release index 1. Its receipt SHA-256 is
`222051e2b36000a0af741784afecc1d16c745712ca1cf5f93d3d1a5ef46e1265`.
Four subsequent hosted runs archived and verified asset indices 3–6 for release
index 1 without any new source retrieval during this reconciliation. Their run
IDs, artifact digests and receipt-file hashes are committed in the cursor. The
seven observed archived assets total 726,797,932 bytes.

The committed cursor resumes at release index 1, asset index 7 when workflow
coordinates are empty. Explicit paired coordinates permit bounded replay. A
hosted success does not mutate the cursor: each receipt requires review and a
normal validated cursor update.

- dispatch bounded MONDO batches incrementally and retain every exact receipt;
- prioritize small provenance/checksum/diff assets before multi-hundred-MB
  ontology serializations, unless a downstream use justifies the storage;
- version a new ClinVar protocol before adding seeds, increasing depth or
  interpreting submitter-derived product rights;
- do not claim complete historical materialization, comprehensive products,
  clinical validity or unrestricted ClinVar redistribution.
