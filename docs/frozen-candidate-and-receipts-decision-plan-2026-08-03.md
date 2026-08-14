# Frozen candidate and qualifying receipts decision plan

**Status:** decision-ready preparation; no gate is approved by this document.
**Revision:** 2026-08-03

## Decision to make

Choose how to establish the candidate identity and obtain the six qualifying
accountable receipts required before any stable-release claim:

1. scientific/source-methods;
2. patient/community;
3. custodian/data governance;
4. independent operator;
5. operational owners; and
6. release authority.

## Options

### Option A — Recommended: narrow, digest-bound release candidate

Freeze a bounded synthetic/public-data candidate first, then request receipts
against that exact identity. Keep restricted, unverified, or unlicensed sources
out of scope. Collect scientific and custodian dispositions before patient or
release decisions; collect independent-operator and owner receipts after the
candidate is frozen.

**Advantages:** smallest evidence surface, least rework, clearest audit trail,
and a credible bounded-release decision even if broader claims remain deferred.

**Trade-offs:** does not close claims requiring live or restricted sources, and
any candidate change invalidates affected receipts.

### Option B — Recommended only if authorities are already available: parallel
full-scope candidate

Freeze the complete intended scope and issue all six requests in parallel.

**Advantages:** shorter elapsed collection time.

**Trade-offs:** larger review burden and high rework risk; one source-term,
protocol or scope change can invalidate every receipt. No gate may be inferred
from a partial response.

### Option C — Safe fallback: preparation-only preview

Keep the current branch and register pending, publish only synthetic methods,
fixtures and draft packets, and do not create a release candidate or stable
tag.

**Advantages:** no authority or source-rights assumptions.

**Trade-offs:** no empirical claims, production support promise, independent
release claim or stable-v1 publication.

## Recommendation and rationale

Choose Option A. The repository already has deterministic synthetic coverage,
receipt schemas and a fail-closed register, but the current branch is not a
real frozen candidate. Narrowing the candidate makes the accountable questions
answerable and prevents a receipt for one scope being reused for another.
Option C is the automatic contingency if an accountable authority or lawful
source evidence cannot be obtained. Option B should be used only when all
participants have confirmed availability and the scope is genuinely frozen.

## Execution sequence

1. **Scope decision:** record included sources, excluded sources, supported
   claims, prohibited claims and intended disposition (`bounded` is the default
   if broader evidence is absent).
2. **Candidate build:** create a clean-clone candidate from an immutable commit,
   generate source/release/package/SBOM/provenance manifests and record all
   SHA-256 digests.
3. **Candidate freeze:** update the receipt register with the exact commit/tag,
   manifest ID and input-manifest digest; prohibit candidate-bound changes.
4. **Panel preparation:** use the subagent panel to inspect completeness,
   identify contradictions and prepare role-specific questions. Panel output
   does not satisfy an accountable gate.
5. **Accountable collection:** route each packet to the relevant authority and
   require a signed or otherwise durable approval record, conditions, dissent,
   residual-risk owner and expiry date.
6. **Administrative verification:** run the receipt and register validators,
   compare candidate identity and digests, check expiry/supersession, and record
   only redacted locator metadata in Git.
7. **Decision reconciliation:** unresolved or conflicting receipts keep the
   affected gate pending and suspend the affected claim. Only the release
   authority may select `release`, `bounded`, `revise` or `stop`.
8. **Publication boundary:** tag or publish only within the final decision;
   retain a draft candidate and all superseded evidence for audit.

## Contingencies

| Situation | Response | Result |
| --- | --- | --- |
| No authority available | Keep gate `pending`; use Option C | No release or approval claim |
| Candidate changes | Rebuild manifests and reissue affected receipts | Previous receipts become superseded |
| Source terms drift | Quarantine source and request custodian re-disposition | Source remains inactive |
| Conflicting receipts | Preserve both, record dissent, suspend claim | No automatic reconciliation |
| Operator cannot reproduce | Record failure and defect; narrow or revise | No independent-release claim |
| Owners cannot accept support | Remove support promise and production pathway | Maintainer-only preparation |
| Release authority chooses `bounded` | Publish only explicitly permitted scope | Stable/full-scope release remains blocked |

## Decisions required from the accountable owner

- Select Option A, B or C (recommendation: A).
- Confirm the bounded candidate scope and exclusions.
- Identify the accountable authority/body for each gate and its secure return
  channel.
- Set any expiry or review date for the receipts.

These decisions select a workflow; they do not themselves constitute the six
independent or accountable receipts.
