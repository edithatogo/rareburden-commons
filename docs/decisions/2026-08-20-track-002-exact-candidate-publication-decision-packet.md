# Track 002 exact-candidate publication decision packet

**Status:** Pending repository-owner decision

**Decision capacity:** Repository owner/operator

**Preparation date:** 2026-08-20

**Evidence commit:** `c99f6361345774604f6b877607943465ef0a3796`

## Exact candidate

The verified candidate contains only the two Orphadata Science July 2026 files
and three MONDO `v2026-08-04` files approved for preparation. Its deterministic
PAX tar stream is 591,841,280 bytes with SHA-256
`1a8e0a01467a56eee0a85f15f971b0dd03820abfa518cc981d6588a264c58cd1`.
The stream was verified and deleted; it has not been published or retained.

Evidence bindings:

- scope SHA-256:
  `dfa41ccb7678791595ebd0045d91a7f9b172389a379e84dfabfb8f9ae8a81b97`;
- verification receipt SHA-256:
  `56d63626de61ef70c728b0ac23dad9521e0c0000470ea3dd7c4c539527a98cac`;
- rights/attribution audit SHA-256:
  `d6a9a068c21701bf80bf9cfb17fd4d52fc880f10ad85efc59c5c706c706fe4f3`.

## Owner options

### Option A — Authorize exact bounded publication (recommended if publication is intended)

Authorize a later external publication action for only the five hash-identified
source files, `MANIFEST.json` and `NOTICE.md`. The publication operator must
rebuild the package from the same publisher releases and stop unless the tar
stream again matches the package size and SHA-256 above.

Trade-off: this produces the approved minimal public source snapshot, but
relies on the publishers' CC BY 4.0 representations. It is not an independent
chain-of-title review of every embedded MONDO assertion. It supports only
bounded source-snapshot and provenance claims.

Contingencies:

- Before any external action, reconcile this evidence branch non-destructively
  with current `origin/main` and the divergent same-name remote branch, remove
  no unique work, regenerate runtime assets and pass the full repository gate.
  If reconciliation changes the evidence commit or candidate inputs, obtain a
  newly bound owner decision; do not reuse this packet as approval.
- Any size, hash, terms, redirect or notice drift returns the decision to
  preparation; no substitution is permitted.
- WPP, WHO GHE, HPO, PanelApp, controlled/credentialed sources and every other
  source remain excluded.
- The already-public WPP object requires separate external-remediation
  authority and verification; this option does not authorize that action.
- Publication does not close Issue #2, Track 002, Track 007 or the v0.3.0
  release gate.

Minimum owner evidence: review the evidence commit, exact package hash,
publisher-reliance limitation, exclusions and bounded-claims list; then record
an explicit `authorize_exact_bounded_publication` decision in repository-owner
capacity. Destination, upload/push authority and post-publication verification
must be separately explicit before external mutation.

### Option B — Defer publication and preserve evidence only

Keep the verified receipt, audit and code while publishing no source bytes.

Trade-off: avoids current redistribution exposure and allows later review, but
the live package must be rebuilt and reverified because no candidate bytes are
retained.

Contingency: any later decision requires current terms observation and the same
exact package hash, or a new scope decision.

Minimum owner evidence: record `defer_publication` with any review date or
trigger. No external-action authority is needed.

### Option C — Reject or supersede this candidate

Do not publish this candidate and require a new allowlist or rights position.

Trade-off: maximizes caution but discards this package as the intended release
candidate; the verification receipt remains historical evidence.

Contingency: a successor must use a new decision ID, exact artifact list,
rights audit, package receipt and bounded-claims disposition.

Minimum owner evidence: record `reject_or_supersede_candidate` and identify the
reason or successor decision. No external-action authority is implied.

## Claims that remain prohibited under every option

The candidate does not establish comprehensive or systematic coverage, global
representativeness, confirmed novelty, independent scientific review,
community authority, clinical validation, partnership, data access or external
approval. Track 007 remains In review. Attribution does not imply endorsement
by Orphadata, Orphanet, MONDO, the Monarch Initiative or any contributor.

## Current decision state

No option has been selected in this packet. Publication, push/upload, issue
closure, release tagging and WPP remediation remain unauthorized.
