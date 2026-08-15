# Track 002 MedDRA and MLDS preparation frontier — 2026-08-16

## Public official evidence

MedDRA is a licensed ICH terminology distributed by the MSSO. The official
subscription form states that subscriptions include English and all available
translations. The official user portfolio says terminology downloads require a
MedDRA ID and password, selection of the release and language, and a
release-specific unzip password. Public v28.1 release documentation reports 27
deployed languages. The official temporary site currently exposes v29.0 support
documentation, but release-file access remains authenticated. None of these
public observations establishes which releases the owner's subscription exposes
or whether its exact agreement permits private cloud storage.

MLDS is SNOMED International's licensing and distribution portal. Official
guidance says affiliates can access approved packages only after accepting the
applicable licence. Member/national centres may impose additional conditions;
non-member-territory use requires annual reporting and may incur fees. Native
international, national, extension, map and language-reference-set releases
must therefore be inventoried independently. UTS-hosted SNOMED files are not a
substitute for the native MLDS inventory.

## Prepared contract

An operator records one exact artifact per product, release, edition,
jurisdiction and language in `licensed-portal-inventory.schema.json`. Every raw
artifact requires its exact byte count and SHA-256, an approved official HTTPS
download URL, agreement identifier, affirmative private-cloud decision and
decision evidence. Metadata-only rows cannot enter the archive workflow.

The destination is fixed to the existing private mixed-rights dataset
`edithatogo/hpo-licensed-ontology-archive`. Existing UTS/SNOMED artifacts are
referenced by exact remote path and size instead of uploaded again. Each run is
manual, limited to three artifacts and 8 GB, paced sequentially by at least two
seconds, rejects cross-host redirects, verifies hashes and remote sizes, and
uses temporary runner storage that is discarded after the job. Public
redistribution, portal completeness, native-edition completeness and production
activation remain false in every receipt.

## Operator login and inventory procedure

1. Sign in interactively at the official MedDRA or MLDS portal. Do not paste a
   password, session cookie, unzip password or token into Git, an issue, a
   manifest, a workflow input or an Actions artifact.
2. Record the exact agreement/version shown to the account and determine whether
   owner-controlled private cloud storage is permitted. If the agreement is
   silent or ambiguous, record `pending`; do not dispatch archival.
3. Enumerate every portal-visible product, release, edition, jurisdiction and
   language. Record factual metadata in a reviewed inventory; do not claim that
   the account exposes all publisher history.
4. For an approved file, record its official same-host download URL, expected
   size and publisher checksum. If no publisher SHA-256 exists, download once
   in the authorized session, compute SHA-256 without committing bytes, and
   record how it was derived.
5. Search existing private archive receipts for the same SHA-256. Use
   `already_archived` plus the exact existing path for duplicates.
6. Store the portal authorization value only as the encrypted GitHub secret
   `LICENSED_PORTAL_AUTHORIZATION`; store the Hugging Face token only as
   `HF_TOKEN`. The workflow does not echo either value.
7. Dispatch only after the inventory has the authorized naming prefix and the
   `terms_confirmed` checkbox is true. Stop on login challenge, changed terms,
   missing checksum, HTTP 429, unexpected redirect, size/hash mismatch, public
   destination visibility or unclear cloud-storage authority.

No portal login, package enumeration or terminology download was performed by
this repository preparation slice.
