# Track 002 private archive capacity blocker

GitHub Actions run `31897934633` attempted one bounded historical UTS artifact
for `umls-metathesaurus-full-subset`. The Hugging Face LFS batch endpoint
returned HTTP 403 with the explicit classification “Private repository storage
limit reached”. The source download had completed in ephemeral runner storage,
but no upload receipt or remotely verified artifact was created.

The checked-in capacity state is therefore `blocked`. Historical workflows now
evaluate it before Hugging Face authentication, remote cursor planning or any
UTS download. A blocked run writes a redacted receipt with
`cursor_advanced:false`, `source_download_started:false` and
`redownload_permitted:false`; the receipt-upload step runs even when the archive
step exits with the dedicated blocked status.

Capacity restoration does not itself prove enough room for an arbitrary batch.
Before changing the state to `ready`, record an authenticated destination
capacity observation, its timestamp and a short expiry, then use a one-artifact
bounded canary. If the LFS endpoint again reports a quota failure, restore
`blocked` without advancing the family cursor. Do not rerun the failed source
download while this state remains blocked.
