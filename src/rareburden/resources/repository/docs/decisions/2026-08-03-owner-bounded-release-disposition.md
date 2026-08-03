# Owner bounded release disposition — 2026-08-03

**Disposition:** `bounded` (repository-owner decision; not a qualifying
external release receipt)

## Authority boundary

The repository is operated as a single-developer project under ADR-0008. The
repository owner is recorded here as `repository_owner_release_decider` for a
time-limited synthetic/public candidate disposition. This decision is not
independent scientific, patient/community, custodian, security, operational or
external approval, and it does not authorize stable-v1 release.

## Candidate binding

- Repository: `edithatogo/rareburden-commons`
- Candidate tag: `candidate-2026-08-03`
- Peeled commit: `9e668ce9dc860daeb45dac135b58ba203d30b239`
- Manifest: `rel-b213c531a6b754940f80ab70`
- Input manifest SHA-256: `d3aafd7367609050d6a4c9926a8ddca3013085362f78abd319dd582135612389`
- Decision date: 2026-08-03 (Australia/Sydney)
- Review/expiry: 2026-09-03, or immediately on candidate change or trigger

## Permitted scope

This disposition permits only synthetic/public preparation, documentation,
metadata/hash artifacts, repository-owned validation, and bounded offline
rehearsals. It makes no production, hosted API, controlled-data, clinical,
patient-facing, global-completeness, endorsement, support-SLA or capacity
promise.

## Stop and revise triggers

- critical or high security, safety, rights or reproducibility finding;
- failed restore, rollback or clean-node validation;
- unresolved source-term or semantic uncertainty affecting a claim;
- package/resource budget breach;
- owner capacity or recovery responsibility becoming unavailable;
- any change to the frozen candidate identity.

On a remediable issue, use `revise` and create a new digest-bound candidate.
For a critical failure, use `stop`. Use `supersede` only after material fixes;
never mutate this candidate's history or receipts.

## Gate status

All six qualifying receipt-register entries remain `pending`. Panel reports,
green CI, local receipts and this owner disposition do not satisfy independent
operator/security, scientific, patient/community, custodian, named-owner or
stable-release authority gates.
