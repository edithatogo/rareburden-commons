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
