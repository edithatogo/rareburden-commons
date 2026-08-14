# Track 014 atlas/API review packet

**Status:** non-binding preparation; Track 014 remains Planned and blocked

This packet turns the Track 014 contract into a bounded evidence request. It
does not activate an atlas, API, beta release, archive, DOI, or redistribution
of third-party data.

The recommended implementation sequence is documented in
`docs/track-014-implementation-plan-2026-08-02.md`: static-first, then a
package and read-only API projection from one immutable release manifest.

## Decisions and accountable evidence

| Decision | Required evidence | Accountable disposition |
|---|---|---|
| Reviewed-artifact boundary | Immutable source/parameter manifest, release fingerprint, and build log showing only reviewed inputs | custodian/data-governance: approve, bound or reject |
| Public-output rights | Licence/terms inventory, redistribution analysis, aggregate-only rule, and removal/supersession procedure | custodian/data-governance: approve or restrict |
| Semantic and statistical display | Evidence-status, uncertainty, quality, missingness and limitation mappings tested against approved source terms | scientific/patient-community panel: approve, revise or stop |
| API/package compatibility | Version policy, schema fixtures, static/package/API consistency receipt and backward-compatibility result | scientific/technical reviewer: pass, revise or bound |
| Accessibility and harm controls | Text alternatives, non-colour-only checks, misuse scenarios and harm mitigations | patient/community reviewer: approve, revise or reject |
| Reproducibility | Clean-environment build, independent operator receipt, checksum comparison and discrepancy log | independent operator: pass, fail or qualified |
| Release decision | Release-content audit, archive/DOI target, residual-risk owners and rollback/correction plan | release authority: release, bounded, revise or stop |

## Evidence format

Receipts must identify the commit/release fingerprint, input manifest digest,
tool/runtime versions, UTC timestamps, commands, outputs and any discrepancy.
Synthetic fixtures may exercise schemas and negative paths, but cannot satisfy
source rights, independent reproduction, scientific suitability or publication
authority.

## Safe continuation

Implement and test schema/build boundaries, consistency checks, accessibility
fixtures and correction metadata locally. Keep the API and beta publication
disabled until the accountable dispositions above are recorded.
