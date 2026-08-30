# Track 003 synthetic scenario arithmetic assurance

Status: implementation preparation only. No new governed demonstrator output,
empirical parameter, clinical claim or release is created by this harness.

`scripts/track003_synthetic_scenarios.py` provides an in-memory function, with no
CLI, file access, source ingestion or persisted results. Its tests use invented
values solely to challenge arithmetic and rejection paths. They are not
additional RBC-P002 analysis executions under the existing one-output receipt.

## Implemented scope

- Change the assumed diabetes denominator while holding a compatible synthetic
  fraction fixed. This tests scaling, not transport between real populations.
- Invert an explicitly assumed binary selection mechanism. For target fraction
  p, selected fraction q and positive selection probability ratio r,
  q = r*p/(1-p+r*p), hence p = q/(q+r*(1-q)). This assumes aligned eligibility
  and perfect classification, not that clinical testing yield is prevalence.
- Partition expected expressed cases into detected and undetected synthetic
  states. Detection is forward conditional probability, specificity is assumed
  one, and neither state is observed diagnosis. Zero detection is allowed here;
  inversion of zero detection remains non-estimable and is not implemented.
- Apply penetrance only to an explicitly supplied person-carrier fraction
  conditional on the same diabetes denominator. Allele frequency is rejected;
  penetrance cannot be applied again to an aetiologic case fraction.

Every result says `synthetic_assumption`, `people` and `not_quantified`.
Deterministic contrasts are not uncertainty intervals. Assumed ranges are not
empirically plausible bounds, and outputs must not be used for clinical advice,
country rankings, population burden claims or resource allocation.

## Still unavailable

Age/calendar alignment, population eligibility, family/cohort dependence and
setting/capture transport remain uncalibrated. No ancestry coefficient, invented
effective sample size, source pooling, complication estimate, utilization
estimate or economic allocation is implemented. Missing evidence is unavailable,
not zero burden. The held source records remain held.

The primary model, seeded uncertainty, exact source/target registration,
provenance-bound execution and report still use the governed engine and ledger
contracts. This small assurance harness is not a substitute for them. Track 003
therefore stays active and its analysis/scenario acceptance tasks stay partial.

## Next decision boundary

The existing dated synthetic disposition permits exactly one persisted output.
A separate candidate-bound decision is needed before further persisted runs.
The recommended route is to qualify a consolidated synthetic scenario execution
candidate; no public-aggregate or controlled inputs are implied. Empirical
qualification remains blocked by compatible-source and transport evidence.
Routine code/test/PR work proceeds under the owner's autonomous-work instruction;
it does not amend the existing output limit or manufacture publisher rights.
