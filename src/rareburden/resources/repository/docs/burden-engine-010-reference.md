# Track 010 synthetic burden-engine reference

This is a non-production reference for the Track 010 alpha surface. It uses
synthetic inputs only and does not activate a source or freeze a downstream
interface.

## Deterministic estimands

`expected_affected_population` multiplies a population interval by a prevalence
proportion and preserves conservative endpoint bounds. `rare_aetiology_cases`
applies the same bounded product to an explicitly compatible case envelope and
aetiology fraction. Both operations reject incompatible units, negative values,
non-finite values and proportions outside `[0, 1]`.

## Uncertainty

`simulate_fraction_product` propagates a beta-distributed fraction through an
exact synthetic envelope. The result records mean, median, 95% interval, draw
count, seed and unit. Reusing the same seed and configuration is deterministic;
the effective sample size is a modelling assumption that must be recorded in
the parameter ledger.

## Missingness and structural scenarios

`assess_analysis_estimability` reports missing parameter identifiers and reasons
without substituting or imputing a value. `run_structural_scenarios` requires a
declared baseline and a bounded set of alternatives, rejects changes to the
analysis identity, estimand, output unit or intended use, and retains each
scenario's ledger and parameter fingerprints. Scenario results are synthetic
assurance records, not an approved scenario set or a formal uncertainty
decomposition.

For independent multiplicative inputs,
`decompose_independent_product` reports left, right and multiplicative
interaction contributions using deterministic Monte Carlo moments, alongside
the empirical product variance and closure error. It explicitly does not support
correlated inputs.

`make burden-benchmark` runs a 10,000-draw synthetic simulation and decomposition,
bounding process CPU time so concurrent host workloads do not create a false
engine regression. This is not an end-to-end wall-latency claim.
It records a digest of the scientific output and enforces a deliberately generous
engineering time envelope. The timing gate detects gross regressions; it is not
evidence that an estimand or distribution is scientifically appropriate.

The public simulation primitives fail closed above 100,000 draws. `make
burden-memory` exercises that ceiling and requires the simulation plus
decomposition workload to remain below a 64 MiB Python-allocation peak measured
with `tracemalloc`. This is a bounded engineering envelope, not a total-process
RSS guarantee or scientific validation.

The assurance suite also includes property bounds, a versioned golden random
vector, seeded convergence toward a known beta mean, and explicit rejection of
overflow and negative simulated products.

## Fail-closed boundaries

The engine rejects direct allocation of a case fraction to DALY, YLD, YLL or cost
envelopes. Those quantities require component-specific onset, severity,
treatment, survival and cost models. No result should be interpreted as a
production burden estimate until Track 009 inputs, semantic definitions and
scientific review are complete.

`run-analysis` is fail-closed to `synthetic_assurance` and requires both an
exact, content-addressed `--quality-disposition` and a
`--source-release-bindings` receipt. The runner rejects non-synthetic semantic
or release identities before computation and validates release provenance via
the bounded wrapper. Exploratory, primary-estimate, policy-decision and public
aggregate execution remain unimplemented and unavailable. Execution results
retain their intended-use and non-authority interpretation, and the bounded
result is labelled `activation_state: not_activated`. Parameter population
and period contexts must match exactly; future compatibility rules require an
explicit contract rather than silent coercion.

Focused implementation coverage is in `tests/test_burden.py`,
`tests/test_burden_assurance.py` and `tests/test_quality_edges.py`; the full
repository validation remains the release gate.
