# Track 010 specification — Public burden engine and uncertainty framework

## Objective

Implement a tested reference engine for expected affected populations, rare-aetiology composition and selected burden modules using ledgered parameters and explicit uncertainty.

## Required outputs

- deterministic calculation contracts;
- supported probability distributions and parameter validation;
- Monte Carlo or posterior-sample propagation with recorded seeds;
- correlation and structural-scenario specification;
- expected affected-population and rare-aetiology calculation modules;
- compatible YLD/YLL/DALY and cost hooks that reject unsupported shortcuts;
- sensitivity, contribution-to-uncertainty and missingness outputs;
- golden, property-based and numerical-stability tests;
- command-line and Python interfaces;
- reproducible reference report from public/synthetic fixtures.

## Acceptance criteria

1. Calculations reproduce from recorded inputs, seed and environment.
2. Invalid fractions, units, populations and incompatible metrics fail clearly.
3. Case fractions cannot be applied to incompatible outcome or cost envelopes without an explicit model.
4. Boundary, convergence and numerical-stability tests pass.
5. Structural scenarios are reported separately from sampling intervals.
6. Every result retains lineage to input parameters and analysis specification.
7. Reference workloads meet documented performance and memory budgets.
8. Independent scientific-software review finds no unresolved blocking issue.

## Non-goals

- a universal disease model that ignores condition-specific natural history;
- opaque composite uncertainty;
- filling missing countries solely to create a complete map;
- clinical prediction for individuals.

## v1 contribution

This track implements V1-MOD-01 to V1-MOD-06 and supplies the common engine for all demonstrators.

## Non-binding protocol draft — burden engine contract v0.1.0 (2026-07-27)

Preparatory only; this does not activate the track or freeze alpha interfaces. Support compatible expected-population and rare-aetiology case-count estimands; outcome and cost estimates require explicit subgroup models. Validate ledger fingerprints, semantic IDs, units, metrics, distributions, dependence rationale, seed and iteration bounds. Propagate fixed, uniform, normal, lognormal and beta uncertainty with recorded seed, engine, iterations and decomposition. Reject direct case-fraction allocation to DALYs, YLD/YLL, deaths or costs and unsupported dependence. Scientific-software, statistical, patient/community and engineering review are required.
