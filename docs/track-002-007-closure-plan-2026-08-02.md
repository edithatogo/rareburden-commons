# Tracks 002 and 007 closure plan

**Recommended route:** Option A — gate-first, bounded scope.

## Sequence

1. Keep Track 002 sources and Track 007 landscape records versioned and
   candidate/provisional.
2. Complete repository-owned panel checks: exact source packets, metric and
   denominator compatibility, search-count reconciliation, deduplication,
   exclusions, claim-to-source mapping, and synthetic negative tests.
3. Submit the Track 002 source packets and Track 007 registration handoff for
   the accountable scientific, custodian and challenge decisions.
4. Reconcile conditions and dissent; narrow or remove unsupported source and
   landscape claims.
5. Only after receipts are digest-bound, run final release validation and decide
   whether v0.3.0 is bounded, revised, or stopped.

## Options and rationale

- **A (recommended):** retain the bounded Orphadata + UN WPP preparation path,
  keep WHO/World Bank candidate-only, and retain Track 007 as a narrow release
  gate. This preserves useful work without overstating evidence.
- **B (safe fallback):** publish a methods/manifest or synthetic-only preview;
  remove novelty, completeness, partnership, endorsement and empirical burden
  claims. This permits progress without external receipts.
- **C (scope reduction):** remove all landscape-derived claims and use only a
  named-source inventory. This is safest if registration or challenge evidence
  cannot be obtained, but requires a formal downstream scope change.

## Contingencies and stop conditions

- Registration unavailable: freeze the versioned protocol and label it
  unregistered; do not call it systematic or complete.
- Search totals drift: append a new dated search log and rescreen; never
  overwrite prior counts.
- Reviewer/challenge evidence unavailable: keep provisional claims and use B.
- Terms or metric incompatibility: keep the source candidate-only or remove it.
- Any novelty, completeness, partnership, endorsement, or community-acceptance
  claim without qualifying evidence: stop and narrow the claim.

Subagent panels implement and challenge repository-owned preparation. They do
not satisfy external authority or independent-operation gates.

The approved Option A scope is machine-readable in
`docs/track-002-option-a-scope.yml`; its activation flag is intentionally
disabled until the required receipts exist.
