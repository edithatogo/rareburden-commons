# Track 013 reproduction evidence reconciliation

Status: bounded mapping of existing evidence to Track 013 acceptance criterion 3.
This is not a new analytical execution, execution authorization, empirical
validation, Track 013 completion or release decision.

## Criterion and exact existing evidence

The [Track 013 specification](../conductor/tracks/013-quality-validation-gap-equity/spec.md)
requires at least one exact analysis candidate to be separately reproduced in an
owner-operated run, with agent challenge and no independent-human-execution
claim. The [Track 003 acceptance record](track-003-reference-closeout-2026-08-31.md)
documents that evidence for the synthetic reference:

- Executed candidate: `36f97490626747b76543f59c44220544978ef874`.
- Candidate tree: `8e70545e1ffa4eb202ad444e3d68d158ce184f82`.
- Candidate manifest SHA-256:
  `b6f50a8b8b10bddceafd16ddaeee17e77fb6eefb8fbfd724cf747378b5a99911`.
- Existing receipt:
  `manifests/demonstrators/track-003-reference-execution-2026-08-31.json`.
- New mapping record:
  `manifests/quality/track013-reproduction-mapping-20260901.json`.

The manifests and retained outputs require the full repository checkout; they
are not installed documentation assets. The new mapping identifies existing
evidence, not another analysis candidate or another pair of runs.

The original primary execution and separate reproduction used distinct clean
checkouts and frozen Python 3.13.13 environments on the same host. Both recorded
successful completion for the same approved inputs, seed and iteration count.
The three immutable outputs under `results/track-003-reference-2026-08-31/`
matched exactly:

- `reference-report.md`:
  `2b1318a462c3ba05e68185e0db03c32320808e10bd82acef824659cc33cabcd2`.
- `reference-results.json`:
  `2045f12db2697d6bba280175470a878a67227a10b34a8542764119c494b9f289`.
- `reference-tables.csv`:
  `315cb384df7be9b2b65387982138f27a6c0a44b4183d12a00407c26cb21dccce`.

The exact Track 003 permission covered the primary run and one separate
reproduction; both permitted runs have already occurred. This reconciliation
does not renew that permission or authorize a third run. Integrity checking and
reading retained files are not analytical reproduction. No historical output,
decision, source snapshot or receipt is rewritten by this mapping.

## Advisory review chain

The current [receipt-specific advisory challenge](reviews/track-013-receipt-challenge-2026-09-01.yml)
records engineering/methods, security/data-use and usability/harm agents directly
inspecting the exact execution receipt and its criterion-level applicability.
It contains each lane's findings and the accept/defer options, trade-offs,
contingencies and recommendation. This current challenge supplies the
receipt-review requirement; the historical panels below are supporting evidence,
not a substitute for receipt-specific advice.

The [original output-panel record](reviews/track-003-reference-output-panel-2026-08-31.yml)
records three advisory perspectives reviewing the actual outputs:

- Scientific/methods: numerical consistency, interpretation and the explicitly
  synthetic applicability/noncomparability assessment.
- Engineering/security/rights: three-file inventory, matching hashes, output
  consistency and absence of empirical source bytes or participant data.
- Simulated community/harm: synthetic labels, conditional uncertainty, unavailable
  burden, fictional costs and limits on causal or policy interpretation.

The [hosted-fixes panel record](reviews/track-003-reference-hosted-fixes-2026-08-31.yml)
supersedes only the checker and closeout bindings. It preserves the original
output review and binds the immutable historical source snapshot. Read both
records together; do not apply superseded checker/document digests to current
files or interpret historical pending-CI labels as new execution permission.

These are simulated role-separated advisory reviews, not independent approval.
Owner-executed simulated-community challenge; no actual community participation,
representation, consultation, endorsement, consent or independent review.

## Disposition and remaining boundaries

Recommendation: accept the existing evidence mapping and complete only the
Track 013 plan task for a separately executed owner-operated reproduction of at
least one analysis. The trade-off is that this provides precise synthetic
reproducibility evidence without establishing empirical accuracy or external
validity. An alternative is to defer that task if any candidate, receipt, output
or superseding-review binding cannot be verified. Do not rerun or alter evidence
to make the mapping pass.

No dissent is recorded against this bounded mapping. Uncertainty about invented
parameters, fixed structural assumptions, source fitness and transportability
remains. Same-host reproduction cannot establish independent or cross-platform
reproduction. It also does not demonstrate real-world diagnostic, clinical,
economic or policy performance.

The monogenic-diabetes and bronchiectasis triangulation tasks, paediatric/economic
validation, and uncertainty decomposition remain open. No independent comparator
is supplied by matching synthetic outputs. Track 013 remains blocked on its
remaining requirements; atlas publication, empirical activation, controlled-data
access and release are not authorized by this reconciliation.

Stop or defer on historical hash drift, mismatched run identity, missing review
bindings, changed output bytes, or claims that numerical agreement establishes
empirical validity, independent execution or actual participation.
