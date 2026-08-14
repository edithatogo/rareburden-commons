# Track 010 burden-engine review packet

**Status:** non-binding preparation; Track 010 remains blocked  
**Contract draft:** burden engine contract v0.1.0  
**Activation rule:** do not freeze alpha interfaces or bind Track 003 until
Track 009 and the required scientific, engineering and patient/community gates
are complete.

## Decisions required

| Decision | Evidence | Accountable disposition |
|---|---|---|
| Estimands and compatible inputs | Synthetic reference, units, populations and invalid-operation tests | approve, revise or reject |
| Uncertainty distributions | Seeded beta propagation, convergence and decomposition reports | approve, revise or bound |
| Dependence and correlation | Explicit unsupported-correlation failure and scenario outputs | approve model, revise or retain bounded exclusion |
| Structural sensitivity | Named scenarios, baseline identity and non-estimability records | approve, revise or reject |
| DALY/YLD/YLL/cost boundaries | Negative shortcut tests and interpretation guidance | approve, narrow or reject |
| Interface/reproducibility | Golden vector, seed/environment records, benchmark and lineage | approve alpha, revise or defer |

## Repository evidence

- Deterministic expected-population and rare-aetiology estimands.
- Seeded uncertainty, structural scenarios, contribution/decomposition and
  explicit non-estimability outputs.
- Fail-closed unit, population, metric, overflow, negative-product and
  prohibited health-loss/cost shortcut tests.
- Lineage-preserving result objects and bounded synthetic benchmark gate.

## Required release packet before alpha freeze

Provide the exact estimand and interface version, ledger/semantic fingerprints,
distribution and dependence rationale, seed/draw configuration, structural
scenario register, numerical-stability and performance receipts, invalid-
operation results, interpretation/communication review, and scientific,
engineering and patient/community dispositions. Synthetic results remain
synthetic and cannot be described as empirical burden estimates.

## Safe continuation

Continue synthetic property, golden, convergence, migration and benchmark
tests. Do not introduce silent imputation, unsupported correlation, direct
case-fraction-to-DALY/cost allocation, or a Track 003 alpha dependency before
the ledger and external review gates are closed.
