# Track 002 external-evidence acquisition plan

**Status:** planning and routing only; no source is activated, cached for
production, redistributed, or treated as scientifically approved.

## Recommendation

Use **Option A — a gate-first evidence packet with bounded parallel work**.
Prepare one digest-bound packet per source, submit the same packet separately to
the scientific and data-governance authorities, and run the source-change
exercise only after the terms disposition is recorded. This gives the smallest
credible evidence chain while preserving a safe fallback for every source.

## Options

| Option | Approach | Benefit | Cost/risk | Decision |
|---|---|---|---|---|
| A | Exact source packet → scientific and custodian decisions → change exercise → activation | Strongest provenance and clearest audit trail | Requires accountable reviewers | **Recommended** |
| B | Continue synthetic adapters and publish a bounded non-production methods release while external packets are pending | Keeps engineering progress moving | Cannot close Track 002 or support empirical claims | Safe contingency |
| C | Narrow v0.3 to World Bank API plus Orphadata, defer UN/WHO | Reduces terms and file-selection complexity | Changes scope and downstream denominator/measure coverage | Use only as a formal bounded decision |

## Dependency sequence

1. **Freeze the candidate set.** Keep the current Orphadata pair, UN WPP 2024
   workbook, WHO GHE file and bounded World Bank query as `candidate_only`.
2. **Build four source packets.** For each, record exact URL/query, publisher
   release, retrieval UTC, MIME/size, SHA-256, geography/year/measure scope,
   licence/terms, attribution, redistribution/cache position, third-party
   material, and intended transformation.
3. **Scientific disposition.** An independent methods authority records source
   suitability, denominator/metric interpretation, coverage, update cadence,
   bias/limitations, and approve/narrow/revise/reject decision.
4. **Data-governance disposition.** A custodian or governance authority records
   lawful purpose, retention/cache rules, redistribution, third-party fields,
   withdrawal/correction conditions, and approve/bound/reject decision.
5. **Run the change exercise.** Against a disposable fixture or newly retrieved
   response, verify changed bytes, changed terms, unavailable route, and
   checksum mismatch all produce a `review_required` record and no production
   manifest.
6. **Reconcile.** Link each receipt to the source-release and acquisition
   manifest IDs; resolve conflicts by narrowing scope or leaving the source
   inactive.
7. **Only then activate.** Update the adapter allow-list and production
   manifest, regenerate downstream lineage, and run the full validation suite.

## Source-specific routes and contingencies

| Source | Primary evidence route | Contingency | Stop condition |
|---|---|---|---|
| Orphadata | Pin the exact same-date epidemiology/alignment XML pair and retain CC BY attribution/change-notice terms | Register manually and use synthetic fixtures only | Release identity or terms cannot be bound to the bytes |
| UN WPP 2024 | Confirm the compact workbook variant, geography/year scope and publication terms against the publisher route | Defer UN and use a bounded denominator source with a formal scope decision | Variant, terms or redistribution position remains ambiguous |
| WHO GHE | Confirm the selected DALY/measure file, third-party credits and WHO public-health terms | Keep WHO as manual/non-redistributed registration; exclude credited fields | Third-party permissions or modification/redistribution conditions are unresolved |
| World Bank | Use the bounded `SP.POP.TOTL` query and record response hash, terms and update cadence | Keep API in probe mode with no production manifest | Query contract, coverage or applicable terms cannot be confirmed |

## Receipt contract

Use `docs/external-gate-receipt-template.yml`. Every receipt must include a
unique ID, accountable authority and role, independence/conflict basis, exact
commit and manifest digest, source packet IDs, evidence references, decision,
conditions, dissent, signature/attestation or durable locator, supersession
pointer, and expiry/review date. Restricted correspondence should be referenced
by a durable locator and hash, never copied into the repository.

## Fallback policy

- If a reviewer is unavailable, keep the source `candidate_only` and continue
  synthetic work; do not infer approval from silence.
- If terms are unclear, choose non-redistribution/manual registration or remove
  the source from v0.3 through a recorded bounded decision.
- If a route changes or disappears, preserve the old receipt, create a
  `review_required` incident, and do not silently replace bytes.
- If scientific and custodian decisions conflict, narrow the supported claim or
  stop the source; do not average or override the decisions.

## Current external boundary

The official WHO page describes GHE as downloadable country/region estimates
covering 2000–2021, while its terms explicitly exclude third-party credited
materials from the general permission and require permission for reuse. The
publisher pages are routing evidence only; they do not constitute the required
Track 002 scientific or data-governance decisions.
