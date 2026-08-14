# Receipt routing and response plan

**Status:** routing preparation; no requests sent and no gate approved.
**Candidate:** `candidate-2026-08-03` / `rel-b213c531a6b754940f80ab70`

## Options

### Option A — Recommended: secure role-separated routing

Send each role-specific packet separately through an agreed secure channel.
Recipients return a completed receipt or a documented inability/conflict. The
maintainer records only redacted locator metadata and digest-checked status.

**Trade-off:** slower than a single combined request, but preserves remit,
independence, confidentiality and an auditable chain of custody.

### Option B — Coordinated batch routing

Send all six packets in one coordinated review window, with each recipient
answering only their own gate.

**Trade-off:** faster, but a candidate change or shared misunderstanding can
invalidate several responses at once.

### Option C — Preparation-only fallback

Do not route externally; retain `prepared_not_sent`, keep all gates pending and
publish only synthetic/draft material.

**Trade-off:** no external claims or stable release, but no authority or
confidentiality assumptions are introduced.

**Recommendation:** Option A. Use Option B only when all recipients confirm
availability and confidentiality arrangements. Use Option C automatically when
no suitable accountable recipient or secure channel exists.

## Routing sequence

1. **Confirm recipients and remit.** Identify the person/body accountable for
   each gate, their authority or independence basis, conflicts, quorum and
   preferred secure return channel. Panels may prepare questions but cannot be
   the accountable authority by substitution.
2. **Issue the frozen packet.** Send the exact request from
   `docs/qualifying-receipt-request-bundle-2026-08-03.yml`, the relevant track
   packet, and the candidate manifest. State that the candidate tag and digest
   must not be changed during review.
3. **Request a bounded response.** Require a decision, evidence reviewed,
   conditions, dissent, residual-risk owner, expiry/review date and durable
   signature or approval record. “No objection” is not a receipt.
4. **Receive securely.** Accept only through the agreed channel. Keep raw or
   restricted material outside public Git; retain a redacted locator and
   SHA-256 where permitted.
5. **Verify administratively.** Run `check_external_receipt.py --require-attributable`
   and `check_qualifying_receipts_register.py --receipt ...`; compare tag,
   manifest and input digest; check expiry and supersession. Do not rewrite the
   submitted decision.
6. **Record status.** Update the register from `pending` only after the receipt
   is complete, attributable, digest-matched, in scope and current. Conflicting
   or incomplete responses remain pending.
7. **Reconcile and release.** Resolve only through the accountable role or
   authority. The release authority alone selects `release`, `bounded`,
   `revise` or `stop` for this candidate.

## Response contingencies

| Situation | Action | Gate outcome |
| --- | --- | --- |
| No response | Send one bounded reminder, then record unavailable | `pending` |
| Conflict of interest | Request replacement or explicit conflict disposition | `pending` |
| Incomplete receipt | Return for correction without editing it | `pending` |
| Digest mismatch | Quarantine response and reissue against current candidate | `pending` |
| Candidate changes | Supersede candidate and all affected requests | `pending` |
| Conflicting decisions | Preserve dissent and suspend affected claims | `pending` |
| Secure channel unavailable | Use Option C | `pending` |
| Bounded decision | Restrict claims and publication exactly to conditions | `bounded` |

## Closeout evidence

For each gate, retain:

- request version and send/return timestamps;
- receipt ID, redacted locator and digest;
- exact candidate tag, manifest and input digest;
- administrative verification result and discrepancy log;
- supersession/expiry status and permitted scope.

The repository must never claim that a panel report, local CI result, owner
approval, silence, or an unsigned draft is an accountable receipt.

