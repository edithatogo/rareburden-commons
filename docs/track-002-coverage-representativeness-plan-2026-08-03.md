# Track 002 coverage and representativeness plan

**Status:** bounded preparation; no completeness or global-representativeness
claim is active.

## Required coverage matrix

For every estimand row, record geography/territory coverage, years and revision
status, population and subgroup coverage, numerator/denominator provenance,
missingness, ascertainment process, uncertainty, likely selection bias and
transportability limits. Distinguish observed, modelled, projected and missing
values; never silently impute or substitute a source.

## Options

### A — Recommended: source-specific coverage matrix

Approve only estimands whose coverage is explicit and whose limitations are
visible in outputs. Keep incomplete or non-comparable rows candidate-only.

**Trade-off:** strongest interpretability and least overclaiming, but narrower
outputs and more metadata work.

### B — Scenario-bounded coverage

Retain additional rows as sensitivity scenarios with explicit missingness and
transportability assumptions.

**Trade-off:** preserves analytical utility but increases interpretation risk;
requires every assumption and scenario to be surfaced.

### C — Synthetic/metadata-only fallback

Publish only coverage templates, hashes, source descriptions and synthetic
fixtures until real coverage evidence is approved.

**Trade-off:** safest but provides no empirical population claim.

## Contingencies and recommendation

If geography/year coverage is incomplete, narrow the claim or leave the row
inactive. If denominators disagree, retain both with a declared comparison and
do not choose a winner silently. If ascertainment or transportability is
uncertain, use descriptive language and sensitivity scenarios. If subgroup or
Indigenous/LMIC coverage is not evidenced, prohibit representativeness claims.
Critical coverage contradictions trigger `revise` or `stop`.

Recommendation: implement Option A, use Option B only for explicitly labelled
sensitivity analysis, and fall back to Option C whenever coverage or bias cannot
be bounded.
