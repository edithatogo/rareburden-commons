# Track 016 independent-operator and security evidence plan

**Status:** repository-owned preparation; independent gates remain pending.
**Candidate:** `candidate-2026-08-03`, peeled commit
`9e668ce9dc860daeb45dac135b58ba203d30b239`.

## Single-developer boundary

The repository owner may execute an attributable owner-operated rehearsal, and
the subagent panel may prepare and challenge the packet. Neither is an
independent operator or independent security authority. The qualifying
register remains `pending` until a receipt meets the applicable independence
and attribution requirements.

## Panel-prepared evidence lanes

1. **Reproduction:** clean locked environment, offline wheelhouse, exact
   commands, environment fingerprint, output hashes and discrepancy log.
2. **Security/supply chain:** threat-model boundaries, dependency/licence/
   secret/static scans, SBOM and provenance verification, tamper tests and
   residual-risk disposition.
3. **Operations:** backup/restore, correction/withdrawal, rollback and incident
   tabletop exercises with redacted, candidate-bound receipts.

The panel records role composition, dissent, expected results, observed
results, unresolved findings and a recommendation. It cannot issue the
qualifying independent receipt.

## Owner-operated fallback

The repo owner may run the same matrix and record `repository_owner_primary_operator`
with no secrets or controlled data. This is valid technical preparation only.
If a real independent operator or security reviewer later becomes available,
their receipt must identify the exact candidate and independently attest to the
commands, outputs, discrepancies and disposition.

## Stop and contingency rules

- Critical/high security, rights, safety or reproducibility finding: `stop`.
- Remediable discrepancy or failed exercise: `revise`, create a new candidate,
  and rerun exact-head checks.
- Missing operator/security participant: retain `pending` and keep production,
  hosted API and stable-v1 pathways disabled.
- Hosted isolated execution may corroborate technical reproducibility, but does
  not itself create accountable independence.

## Required receipt contents

Candidate tag, peeled commit, manifest and input digest; operator identity and
role; environment and tool versions; commands and exit statuses; artifact and
output hashes; findings and dissent; residual-risk owner and expiry; tested
rollback/withdrawal scenarios; and an explicit disposition. Do not retain
credentials, participant records or controlled data.
