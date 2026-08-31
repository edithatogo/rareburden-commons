# Conductor integrity reconciliation

Status: bounded repository-maintenance repair, 31 August 2026. No analytical
execution, new source acquisition, production activation or release is approved
by this document. It implements the owner's instruction to address integrity
issues and the already adopted ADR-0009 review model.

## Canonical state and navigation

- Track 003 is complete in its approved synthetic scope. Setup state no longer
  calls it active; Track 014 is blocked, not planned.
- Track 006 metadata and archive location govern its registry status: archived.
  Its completed historical work is retained, not undone or re-executed.
- Setup `completed_tracks` retains the legacy union of complete and archived
  metadata statuses. `archived_tracks` inventories archive location, including
  bounded-complete Track 015. These fields intentionally overlap; they are not
  disjoint lifecycle buckets. Track 015 is not newly archived or reclassified.
- All 19 tracks have a canonical index linked from the registry. Existing
  specification, plan, review and archive paths remain unchanged.
- Track 016's four unstarted qualifying gates are pending, not in progress.
  Its 49 completed preparation tasks are preserved and it remains planned.

The roadmap checker now recognises in-progress and nested task checkboxes.
The additional mandatory offline integrity check reconciles registry, indexes,
setup-state inventories, archive placement and plan state. Tests deliberately
mutate these projections to prevent recurrence. Native runtime-asset generation
also carries the repaired records into installed packages.

## Prospective review roles, not evidence upgrades

ADR-0009 and the agent-review-panel policy already require role-separated
advisory agents and the sole owner's disposition. Track 004's second-operator
criterion and Track 014's independent-reproduction criterion are aligned with
the roadmap's owner-operated clean-environment reproduction requirement.
Separate execution, documented installation, equivalent results, panel challenge
and owner disposition remain required. No pending task is checked by this change.

Track 014 pending gate identifiers are explicitly superseded as follows:

| Historical identifier | Current pending gate |
|---|---|
| accessibility-independent-review | accessibility-agent-review |
| real-user-usability | usability-agent-challenge |
| independent-reproduction | reproduction-agent-review |

These are review-role corrections, not claims that real-user research or
independent reproduction occurred. The existing satisfied owner-operated
reproduction receipt is unchanged; the pending audit still requires review.
Historical receipts, qualifications and false authority flags are not rewritten.
Real participation, third-party custodian approval, publisher rights, empirical
fitness and external registry events remain evidence-bound facts. A future
supported claim requiring them must obtain actual evidence or remain excluded.

For Track 016, prospective security/operator challenge uses the same agent/owner
model. Old preparation receipts retain their original non-independent labels
and cannot authorize production. Production operations still depend on Tracks
004/014; an exact-candidate owner release decision remains separate.

## Immediate low-blocker work candidates

1. Track 004: audit the documented synthetic offline installation and failure
   paths; add missing adversarial cases and prepare the review packet. No
   controlled node, source acquisition or production activation is required.
2. Track 017 bounded documentation preparation: reconcile public instructions
   with the current CLI and retained Track 003 output paths, test the examples,
   and prepare release-note/migration drafts. Do not tag or claim stable release.
3. Track 005: draft economic perspective/unit/price-year and component-overlap
   contracts with invented fixtures and negative tests. Do not select empirical
   costs, assert clinical validity or freeze an unreviewed estimand.

These are bounded tranches, not promises of whole-track completion. The first
two are principally verification and documentation; Track 005 needs more
scientific judgment. Full Track 004 closure still needs an exact contract,
policy-store integration evidence, review and owner disposition.
