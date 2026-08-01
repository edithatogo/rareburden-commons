# Track 003 synthetic reference specification

**Status:** non-binding repository fixture; not a registered protocol, clinical
definition, empirical estimate, or approved alpha analysis.

## Estimand and states

For a declared geography, period, age band and compatible diabetes denominator,
the reference estimand is the expected number and proportion of people in a
synthetic monogenic-aetiology envelope. The fixture keeps these states distinct:

- **diagnosed:** cases identified by an approved clinical/genetic ascertainment
  process;
- **undiagnosed:** modelled residual cases under an explicitly declared
  ascertainment fraction;
- **modelled:** scenario output produced from ledgered population and fraction
  parameters, without implying that the fraction is observed locally.

The denominator, aetiologic fraction, ascertainment, penetrance and referral
parameters must carry ledger IDs, revisions, uncertainty and population/period
contexts. No case fraction is applied directly to DALY, YLD, YLL or cost
envelopes; those require compatible subgroup models.

## Synthetic fixtures and checks

The reusable fixtures are:

- `examples/semantics/rare-within-common-synthetic.yml`;
- `examples/semantics/orpha-to-synthetic-mapping.yml`;
- `examples/ledger/public-foundation-synthetic.yml`;
- `examples/analyses/expected-population-synthetic.yml`;
- `examples/demonstrators/003-ledger-profile.yml`.

The semantic, ledger, burden and demonstrator-readiness suites validate stable
IDs, provenance, mutually exclusive aggregation, uncertainty, incompatible
operations, missing roles and reproducibility. A profile with unresolved roles
must remain `analysis_ready=false`.

## Scenario boundary

Permitted synthetic sensitivity dimensions are denominator choice, age, ancestry,
setting, ascertainment, penetrance and referral bias. Each scenario must retain
the same analysis identity and declare changed parameters and limitations.
Outcome and economic scenarios remain unbound until compatible evidence and
reviewed subgroup models exist.

This reference is evidence of executable contracts only. It does not establish
clinical validity, prevalence, representativeness, patient acceptability or
permission to run a production analysis.
