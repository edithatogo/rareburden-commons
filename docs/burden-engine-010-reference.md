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

## Fail-closed boundaries

The engine rejects direct allocation of a case fraction to DALY, YLD, YLL or cost
envelopes. Those quantities require component-specific onset, severity,
treatment, survival and cost models. No result should be interpreted as a
production burden estimate until Track 009 inputs, semantic definitions and
scientific review are complete.

Focused implementation coverage is in `tests/test_burden.py`,
`tests/test_burden_assurance.py` and `tests/test_quality_edges.py`; the full
repository validation remains the release gate.
