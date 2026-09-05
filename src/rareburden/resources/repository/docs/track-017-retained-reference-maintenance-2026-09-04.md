# Track 017 retained-reference maintenance contract

**Status:** repository-owned maintenance guidance; no adoption or release claim

This contract governs retained synthetic references and documentation while the
project remains pre-release.

## Source of truth

- Conductor `plan.md`, metadata and registry state are authoritative for task
  status; packaged runtime assets are generated projections.
- A retained report, table or JSON output is an immutable reference only when
  its recorded digest and generation receipt verify.
- Guides must distinguish inspecting retained outputs from generating a new
  analytical run. Inspection must not use overwrite or regeneration flags.
- External web sources are cited by exact release and retrieval evidence;
  changed source terms or releases trigger reassessment, not silent refresh.

## Maintenance actions

1. Run the repository-native integrity and retained-reference checks from a full
   checkout.
2. Compare output manifests and hashes before replacing a retained reference.
3. Update links, citations and limitation language together when a reference is
   superseded.
4. Refresh packaged runtime assets after changes under the repository resource
   projection.
5. Record corrections or withdrawals as new, hash-bound notices; do not rewrite
   historical receipts.

## Explicit boundaries

These maintenance actions do not create a maintainer appointment, backup owner,
support promise, adoption evidence, independent review, publication authority,
stable release, or v1.0.0 tag. They do not authorize controlled-data access or
new empirical execution. A green validation suite is repository readiness only.

## Stop conditions

Stop and route to owner disposition if a digest changes unexpectedly, a source
licence or withdrawal notice changes, a guide implies a release or adoption,
the full checkout is unavailable, or a proposed update would remove uncertainty
or missingness from a retained result.
