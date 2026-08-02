# Qualifying accountable receipts plan

**Status:** executable preparation plan; no receipt or gate is approved by this
document.  **Revision:** 2026-08-03

## Decision options

### Option A — Recommended: packet-by-packet, digest-bound collection

Prepare one packet per gate, bind each request to the same candidate commit,
input manifest and release artefact digests, and collect receipts in dependency
order.  The repository maintainer performs only completeness and digest checks;
the named accountable authority supplies the decision.  This gives the clearest
audit trail and prevents one incomplete receipt from being reused across gates.

### Option B — Parallel collection

Request all independent gates at once against a frozen candidate.  This reduces
elapsed time, but requires re-issuing every affected receipt if the candidate or
source terms change.  Use only when the candidate identity is frozen and every
packet states its own scope.

### Option C — Synthetic-only closeout

Keep all gates pending and publish only synthetic demonstrations and draft
protocols.  This is safe when authorities are unavailable, but does not support
empirical claims, production access, stable-v1 tagging or support promises.

**Recommendation:** use Option A, with Option B for independent operator and
operational-owner packets after the candidate is frozen.  Use Option C as the
automatic contingency when a receipt cannot be obtained.

## Receipt workflow

1. **Freeze the candidate input set.** Record the exact commit/tag, release
   manifest identifier, input-manifest SHA-256, artefact digests and intended
   scope. Do not alter source pins or generated outputs while packets are out.
2. **Prepare packets through the panel.** The repository review panel checks
   completeness, identifies uncertainties and drafts questions. Panel output is
   preparation, never an accountable disposition.
3. **Issue role-specific requests.** Use the blank receipt template and the
   relevant review packet. Require the authority's remit, independence or
   constituency, conflicts, evidence reviewed, decision, conditions, dissent,
   residual-risk owner and expiry/review date.
4. **Receive through a controlled channel.** Store only the durable locator,
   receipt ID, redacted metadata and SHA-256 in Git unless redistribution is
   explicitly permitted. Never commit credentials, personal request data or
   restricted source material.
5. **Verify without changing meaning.** Run the receipt schema and semantic
   validator, compare commit/manifest/digest fields, check supersession and
   expiry, and preserve discrepancies. The maintainer may return an incomplete
   receipt for correction but may not rewrite its decision.
6. **Record status.** Update the gate register from `pending` only when the
   receipt is attributable, digest-matched, in scope and not expired. Record
   the locator and verification result, not private contents.
7. **Reconcile dependencies.** Scientific/source and custodian decisions feed
   002 and 007; semantic/ledger/engine decisions then feed demonstrators;
   operator and owner receipts feed operations; release authority decides only
   after all required upstream receipts are present.
8. **Re-open on change.** Any candidate, source-term, protocol, scope or
   material-risk change invalidates affected receipts and returns them to
   `pending` until reissued or explicitly superseded.

## Gate packet matrix

| Sequence | Gate | Minimum accountable result | If unavailable or conflicting |
| ---: | --- | --- | --- |
| 1 | Scientific/source methods | exact sources, estimands, uncertainty and residual-risk disposition | keep 002/007 provisional; synthetic/public fixtures only |
| 2 | Custodian/data governance | terms, retention, redistribution, withdrawal and pilot boundaries | keep restricted/deferred sources inactive |
| 3 | Patient/community | acceptable use, harm, language, accessibility, equity and dissent | narrow claims; no patient-facing or community endorsement claims |
| 4 | Independent operator | clean reproduction, usability, checksum and discrepancy receipt | maintainer-only rehearsal; no independent-release claim |
| 5 | Operational owners | named primary/backup acceptance, support, incident and recovery scope | no production support promise; retain bounded maintenance mode |
| 6 | Release authority | `release`, `bounded`, `revise` or `stop` for the exact candidate | do not tag or publish stable v1; preserve candidate as draft |

## Contingencies and stop conditions

- **Candidate changes:** invalidate and reissue all digest-bound receipts.
- **Source route or licence changes:** quarantine the affected source, preserve
  the old receipt, and request a new terms disposition.
- **Missing authority or quorum:** keep status `pending`; do not infer consent
  from silence, a panel report, local CI or owner approval.
- **Conflicting decisions:** retain both receipts and dissent, suspend the
  affected claim, and route a bounded reconciliation request to the relevant
  authority.
- **Expired or superseded receipt:** retain it for audit, but it cannot clear a
  gate.
- **Restricted evidence:** record only a redacted locator and digest; do not
  copy controlled material into the public repository.

## Closeout checklist

- [ ] Candidate identity and input manifest frozen.
- [ ] Scientific and custodian/source receipts received and verified.
- [ ] Patient/community receipt received and verified where applicable.
- [ ] Independent operator receipt received and verified.
- [ ] Operational primary/backup acceptance received and verified.
- [ ] Release-authority decision received for the exact candidate.
- [ ] Gate register updated with receipt IDs, locators and verification status.
- [ ] Re-run full local validation and preserve the transcript.
- [ ] Tag or publish only within the recorded release decision and scope.

