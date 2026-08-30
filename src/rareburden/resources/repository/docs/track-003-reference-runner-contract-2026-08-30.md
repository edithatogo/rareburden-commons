# Track 003 reference runner contract

Status: implemented in-memory calculations and reporting preparation, not an
execution receipt, empirical validation or completed track. The original Track
003 scope remains unchanged. Inputs are the eighteen explicitly invented
parameters in `examples/demonstrators/track-003-reference-inputs.json`.

## Numerical contract

`scripts/track003_reference_runner.py` uses the versioned RareBurden random
stream. Every iteration samples canonical inputs in sorted parameter-name order,
then a second independent aetiologic fraction. The same draw feeds all scenarios
to align contrasts. There are no participant records or individual event draws.
The maximum is 10,000 iterations. Reports retain aggregate summaries only.

Deterministic outputs use declared central input values. Nonlinear plug-in
results are not expectations. Simulation intervals are linearly interpolated
2.5th and 97.5th percentiles of invented parameter-uncertainty draws, not empirical
confidence intervals. Fixed design assumptions have no calibrated uncertainty.
Standard deviation uses the sample denominator. No family effective sample size
or independent-person sampling assumption is introduced.

Let N be the compatible diabetes denominator, p the target expressed-case
probability, d detection given case, g person-carrier probability, pi expression
given carrier within diabetes, w younger-stratum share, and h(p,k)=kp/(1-p+kp).

| Scenario | Construction and interpretation |
|---|---|
| primary | C=Np, detected=Cd, undetected=C-Cd; all are modelled expectations |
| denominator_low/high | Multiply N by its registered scale; alternatives, not interval endpoints |
| ascertainment | Set d=1 as a perfect-detection counterfactual; no effect on complications/costs |
| carrier_penetrance | C=Ng*pi; never apply penetrance again to expressed-case p |
| referral_selection | Selected-cohort fraction=h(p,r); preserve target C=Np; referral counts unavailable |
| age_stratified | C=N[w*h(p,k_y)+(1-w)*h(p,k_a)]; disjoint 0-19 and 20-100 strata |
| calendar_2030 | Replace p with h(p,k_time); denominator held fixed; constant fictional 2025 prices |
| model_eligibility | Estimate only covered N*m; uncovered aetiology unavailable, not zero |
| unclassified | Estimate only classified N*(1-u); unknown contribution unavailable, not zero |
| strata_independent | C=N[w*p1+(1-w)*p2], independent fraction draws, shared N and d |
| strata_shared | Shared p in unnamed disjoint strata; exactly the primary model |

Age multipliers change the weighted probability; they do not calibrate strata
back to the primary probability. Model eligibility is an ancestry-applicability
stress test without biological ancestry coefficients or extrapolation into an
uncovered population. Scenario context explicitly records hypothetical transfer
assumptions, base parameter IDs and the perfect-detection override. These are not
new empirical transportability judgements.

## Outcomes, units and empty populations

Treatment changes equal detected people times an invented change probability;
they imply neither benefit nor adherence. Hypothetical annual complication
people equal C times the assumed probability: all cases are event-free at year
start and fully followed, with at most one composite event. Annual costs equal
C full case-years times the invented cost per case-year, in fictional currency.
Do not sum overlapping treatment and complication groups or attribute a general
cost envelope by case fraction.

Historical delay is an assumed conditional interval, not an observed average or
necessarily an interval within the reference year. All conditional probabilities
and delay fields have `assumed_` names, including when the conditioning set has
zero expected people. No undefined empirical rate is invented. Metric metadata
accompanies each numeric field with units and conditioning scope. Within-diabetes
probabilities are not total-population prevalence; observed diagnosis is absent.

## Evidence comparison and family disposition

The existing, attributed descriptive ledgers remain separate from these inputs:

- `docs/track-003-outcome-service-ledger-2026-08-30.yml`: source-defined duration
  from diabetes diagnosis to genetic testing and selected post-diagnosis treatment
  change have different endpoints/populations from the fictional delay and change
  scenarios. Their shared cohort cannot supply independent validation or pooling.
- `docs/track-003-licensed-pathway-evidence-2026-08-30.yml`: final genetic yield
  among selected adult probands differs from target-population aetiologic
  probability and from a simple referral mechanism. It does not validate the
  chosen referral ratio or provide general service-use intensity.
- `docs/track-003-additional-source-screen-2026-08-30.md`: complication and
  family/age leads remain unpromoted. Rights, endpoints, ascertainment and
  correction limitations are not repaired by this synthetic demonstrator.

This is an applicability comparison, not agreement testing or an empirical
validation claim. Diagnosis delay, treatment, complications and service-use
families have explicit inventory/hold dispositions; no qualified service-use
rate or empirically calibrated complication/cost model is available. Synthetic
outcome scenarios are allowed by the specification but do not close those
external evidence gaps. Final acceptance review must judge this disposition.

## Remaining execution gate

The full candidate must bind code, input and evidence hashes, scenario contexts,
seed, iteration count, exact output inventory and reproduction instructions.
Required scientific, engineering and simulated-harm review and owner disposition
precede retained governed execution. Historical receipts remain unchanged.
Subsequent report/package and separate clean-environment reproduction must be
verified before marking Track 003 complete.
