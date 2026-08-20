# External gate evidence index

**Status:** legacy routing index; additional-person review lanes were
superseded for repository review by ADR-0009. Publisher rights and any future
controlled-data custodian terms remain factual external constraints.

This index is a routing document for accountable evidence. It does not record
approval, consent, appointment, independent reproduction or release authority.

| Gate owner | Required submission | Repository route |
|---|---|---|
| Scientific methods authority | Methods disposition, estimand/uncertainty review, residual-risk decision and expiry | Tracks 002, 003, 005, 007, 008, 009, 010, 011, 012, 013 packets |
| Patient/community authority | Acceptable-use, harm, stigma, accessibility and benefit-sharing decision with dissent | Tracks 003, 005, 010, 011, 012, 013, 015, 017 packets |
| Custodian/data-governance authority | Source terms, redistribution/aggregation limits, Indigenous/CARE conditions, correction/withdrawal route | Tracks 002, 004, 008, 009, 012, 014, 015 packets |
| Independent operator | Clean-environment build/run, checksum comparison, discrepancy log and usability receipt | Tracks 004, 014, 016, 017 packets |
| Named operational owners | Primary/backup roster, incident, recovery, support and succession acceptance | Tracks 016 and 017 packets |
| Release authority | Release-content audit, residual-risk disposition and release/bounded/revise/stop decision | Tracks 014, 016 and 017 packets |

## Receipt minimum

Every submission should identify a unique receipt ID, accountable person/body
and role, organisation or constituency, decision date, quorum or independence
basis, conflicts, exact commit/tag and manifest/input digest, environment and
commands, retained outputs, discrepancies, conditions, dissent, expiry/review
date, superseded receipt (if any), and any restricted evidence pointer. Return
receipts through the agreed secure channel; record only the durable locator and
digest-checked status in the repository register.

Drafts, synthetic fixtures, local CI, hosted CI and subagent panels remain
repository preparation only. They must not be relabelled as external approval.

Use `docs/external-gate-receipt-template.yml` as the starting shape for a
submission; replace every blank with an accountable, digest-bound receipt.
For the current Track 017 contract, use
`docs/track-017-evidence-contract-reconciliation-2026-08-20.md` and the
hash-bound manifests under `manifests/release/`. The older
`docs/external-gate-register-017.md` and `docs/external-review-request-017.md`
are retained as legacy templates; they do not add an additional-person gate.
