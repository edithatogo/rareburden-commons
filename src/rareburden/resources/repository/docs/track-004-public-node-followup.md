# Track 004 real-public-data follow-up

Purpose: record the additive real-data candidate, not extend the historical
synthetic acceptance receipt. Status: repository-owned implementation and bounded
validation completed; exact-candidate owner acceptance and release remain pending.

## Work and acceptance boundary

The owner's instruction to complete the remaining work authorises preparation
and testing of the previously identified survey, installation and recovery work.
It is not retrospectively attached to an unreviewed candidate as a release
decision. The sole accountable human remains `edithatogo`.

- Survey-aware NHANES questionnaire analysis: methods contract and validation.
- Complete hash-locked runtime: platform-specific, installed-package evidence.
- Durable local delivery: crash tests and recovery without recomputation.
- Role-separated advisory challenge, fixes, full repository validation and
  an exact-bound decision packet for the owner.

No new controlled source, third-party custodian, clinical authority or actual
community participation is created. Real public-use data do not identify
monogenic diabetes. UCI encounter counts and NHANES self-reported diagnosis
answer distinct questions; they are not pooled or linked to each other.

## Durable local delivery contract

`rareburden.public_delivery` serializes only the caller's already
disclosure-checked result. It is not a general disclosure validator. The supplied
runner only passes results from its fixed analysis functions.

The runner exclusively creates a new rehearsal directory beneath an existing
trusted parent and fsyncs the parent directory entry. It reserves each
analysis before calculation. It writes `results.staged.json`, flushes and fsyncs
it and its directory, then writes and syncs `results.sha256`. Publication uses
a same-filesystem hard link to `results.json`, atomically refusing replacement.
The directory is synced again. The stage and digest are retained.

Recovery validates staged bytes against the retained digest and publishes the
same bytes. An existing byte-identical result is an idempotent success; a
different result, symbolic link, missing receipt or digest mismatch fails.
Recovery does not read source records, import pandas, open/reset a policy store,
reserve another query or recompute a result. A failure before a valid durable
stage and digest exist requires inspection; no automatic retry is permitted.

```sh
python -I -m rareburden.public_node_cli --output /existing/rehearsal --recover
```

This qualifies only an owner-controlled local POSIX filesystem with hard-link
and fsync support. It is not a digital signature, external custodian delivery,
network-filesystem guarantee or defence against a privileged actor replacing
both bytes and hashes. Keep the directory, stage, receipt and SQLite store
together, do not edit hard-linked results, and restrict write access. Power-loss
behaviour of storage hardware is not established by injected process failures.

## Evidence and decision

The earlier [descriptive tranche](track-004-public-counts-2026-09-06.md) is a
historical execution receipt. Its then-pending items are resolved only by the
new evidence recorded here and in the linked method/installation records.
No previous synthetic owner disposition is reused for the real-data candidate.

The survey runner additionally pins `data/DEMO_L.parquet` at SHA-256
`24f3623742b1900911bc49b6fcaa0786a9eb3a486dd2d4e86a126514d427ac4f`
in the same immutable NHANES mirror revision
`1b5a370cb2e3bca31b9559238817c4eb21b00070`. Its preserved raw `DEMO_L.xpt`
has SHA-256 `ca4374a158b493b8b0163e1388da21d57a18d1b9cecff2aa4e2fa2bec494fe23`.
The mirror's manifest and conversion script record format conversion with no
filtering, joins or imputation. The runner checks retained bytes before decoding.

The combined experimental outputs are not an approved public statistical
release. Separate count and survey query identities do not constitute a joint
disclosure guarantee. Hypothetical disclosure tests use invented fixtures only;
no NCHS re-identification or disclosure-method attack is performed. Follow the
[NCHS Data User Agreement](https://www.cdc.gov/nchs/policy/data-user-agreement.html).

## Real execution and recovered delivery

The initial survey rehearsal stopped on fractional `RIDAGEYR` values before
survey reservation. Its two already committed descriptive reservations remain
in `node-survey-rehearsal-20260906-a` under the external data root; no database
was reset. Investigation found no missing ages and fractional values only below
one. Raw XPT read through pandas matched the Parquet conversion. The corrected
contract preserves sub-one values without rounding, keeps their design rows
and excludes them from the adult domain. See the
[method and tests](track-004-public-survey-method.md) for the explicit boundary.

The corrected rehearsal `node-survey-rehearsal-20260906-b` succeeded with the
three fixed analyses. `results.json` SHA-256 is
`2d1fb9fe32177a689793641adecb9cc38d90bd8e642a22d4430bee087898ac21`.
The subsequent source-checkout module recovery invocation retained exactly those
bytes. These are same-host local evidence, not a public release or fresh
installation proof. The [separate installed proof](track-004-public-node-installation.md)
records its own exact wheel, dependency capsule and result receipts.

## Final verification and advisory disposition

- `make PYTHON=.venv/bin/python check` passed with 2,198 tests, including 72
  focused public-node, survey, delivery, CLI and installation-verifier tests.
  Ruff, formatting, strict typing, documentation links, safety and Conductor
  integrity passed. Generated runtime references are synchronized separately
  after recording the final evidence.
- The final [installed proof](track-004-public-node-installation.md) installs
  the exact 15-wheel application/runtime capsule into a fresh environment with
  no package cache or index and enforced network denial. Installed execution
  and recovery pass, including the parent-directory fsync implementation.
- The [R software crosscheck](track-004-public-survey-reference.md) agrees on
  the real fixed ratio and Taylor SE, plus two hand-calculated invented cases.
  R independently decodes the XPT inputs. This closes algorithmic agreement
  for this estimator, not clinical validity or NCHS reliability qualification.

Simulated engineering/security advice found one parent-directory durability
defect, now resolved and re-reviewed. Simulated rights/data-use and community
impact advice led to immutable interpretation metadata, local-export wording,
explicit DEMO provenance and source-use limits. The statistical implementation
has hand-calculated tests plus a separate R calculation. These are advisory
agent roles, not independent people, community representatives or approvals.

Recommendation: accept the exact candidate as an experimental real-public-data
execution toolkit while withholding a substantive public population estimate
and production/custodian claims. The alternative is to defer acceptance and
retain all evidence locally. Before publishing statistical findings, complete
the NCHS reliability assessment and joint output-disclosure disposition; do not
infer either from software agreement or minimum-cell thresholds. An actual
controlled-node deployment needs its actual environment and custodian evidence.
No additional human approver is proposed: the owner alone decides repository
scope and release, while third-party facts remain evidence-bound.
