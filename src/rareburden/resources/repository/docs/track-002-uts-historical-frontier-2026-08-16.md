# Track 002 historical UTS archive frontier

This is the bounded continuation contract for the 2,437 historical artifacts
that remained after the current release from all 14 UTS families was archived.
Licensed payloads go only to the private
`edithatogo/hpo-licensed-ontology-archive` dataset. GitHub retains code,
non-secret manifests and redacted receipts, never licensed bytes or credentials.

## Confirmed checkpoint

GitHub Actions run
[`31893681893`](https://github.com/edithatogo/rareburden-commons/actions/runs/31893681893)
successfully archived MRCONSO indices 1 through 5: releases `2025AB` through
`2023AB`, 2,233,759,449 bytes in total. The private archive contains the five
exact payloads plus receipt range `00001-00005.json`. The next observed MRCONSO
cursor is index 6. This is a family checkpoint, not a claim that other families
or historical releases are complete.

## Resumption contract

`scripts/archive_uts_historical_frontier.py` reads the private archive's remote
file listing before each run. An index is skipped only when both its exact
payload and a covering receipt range exist. Payload-without-receipt or
receipt-without-payload is an error; the runner never guesses or overwrites the
checkpoint. Current index zero is excluded from the historical frontier.

Each artifact is downloaded, hashed, uploaded, remotely size-verified and
discarded before the next artifact. Requests remain sequential and inherit the
two-second UTS pacing, `Retry-After` handling and bounded exponential backoff.
The overall run stops before starting another artifact when its artifact,
elapsed-time or byte budget is exhausted. A single unexpectedly large artifact
fails before upload when it exceeds the remaining byte budget.

## Dispatch and cost policy

The workflow is deliberately manual. No cron is enabled because artifact sizes
vary materially and unattended execution could create unexpected GitHub Actions
or private Hugging Face storage costs.

Recommended cadence:

1. Dispatch one run with `max_artifacts=1` for a new family or after a failure.
2. Inspect the redacted Actions receipt and private remote checkpoint.
3. Increase to the default `max_artifacts=3` only when observed sizes fit the
   eight-gigabyte and 180-minute budgets.
4. Never queue multiple runs: GitHub concurrency retains at most one running
   and one pending job, so repeated dispatches can replace pending work.
5. Run `family=auto` only for the configured order; use an exact family slug to
   continue or diagnose one family.

The workflow maximums are 10 artifacts, 8 GB and 210 script minutes inside a
240-minute job timeout. Raising them is a policy change requiring a reviewed
commit, not an ad hoc dispatch value.

## Claims and stop conditions

UTS, RxNorm and SNOMED bytes remain private licensed material. UTS inclusion
does not prove native national-edition, language, country or terminology
completeness and does not activate a production or clinical use.

Stop on credential failure, non-private destination, provider rate response
after bounded retries, unsafe or changed manifest fields, payload/receipt
mismatch, byte/time budget exhaustion, remote size-verification failure,
licence change, or unexpected cost/storage growth. Preserve the last verified
cursor and start a new bounded run after remediation; never infer completion.
