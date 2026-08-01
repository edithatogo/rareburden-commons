# Track 013 assurance protocol draft

**Status:** repository-owned draft; not an empirical validation, registered
protocol, independent reproduction, or approval of an atlas release.

This document defines validation types, calibration decision rules, model
criticism, and evidence-maturity language. It is intended for synthetic and
reference runs first and remains fail-closed when prerequisite demonstrators or
external reviewers are unavailable.

## Validation types

| Type | Question | Minimum evidence | Release consequence |
| --- | --- | --- | --- |
| Internal consistency | Do schemas, units, bounds, lineage and deterministic reruns agree? | Validated manifests, negative tests, repeat-run digest | Required for every release; failure blocks release |
| Internal validation | Does the implementation reproduce held-out or resampled reference inputs? | Frozen split/resampling plan, prediction-v-observation report, code and seed | Required for modelled estimates; otherwise mark unvalidated |
| External validation | Does an estimate agree with an independent population, registry or study? | Independent source, compatible estimand, transportability assessment and comparison | Required before comparative or target-population claims |
| Predictive validation | Does a prospective or temporal holdout remain calibrated? | Time-split predictions, calibration report and drift assessment | Required before forecasting or operational deployment |
| Face/content validity | Do domain and community reviewers judge definitions and interpretation fit? | Named reviewers, conflicts, comments, disposition and dissent | Required for patient-facing or policy interpretation |
| Sensitivity/model criticism | Which assumptions or missingness mechanisms change the conclusion? | Decision-sensitive parameter report and challenged alternatives | Material unresolved sensitivity narrows release language |

## Calibration and criticism rules

Calibration thresholds are decision rules, not universal scientific constants. A
comparison is eligible only when estimand, unit, population, geography and period
are compatible. Reports include point estimate, uncertainty interval, calibration
slope/intercept where relevant, absolute and relative error, and the predeclared
decision threshold.

- **Pass:** the observed value is covered by the 95% interval and absolute error
  is within the approved domain threshold.
- **Review:** interval coverage holds but error exceeds the threshold, or the
  comparison is small or transport-limited.
- **Fail:** interval coverage fails, the estimand is incompatible, or material
  bias/coding error is identified.
- **Not assessed:** no compatible independent reference exists; this is not a
  pass and cannot support a global or comparative claim.

Every criticism states the challenged assumption, affected parameters, direction
of possible bias, scenario or re-fit performed, and whether the decision changes.
No weighted composite quality score may hide a failed domain.

## Evidence-maturity release language

| Maturity | Permitted language | Prohibited language |
| --- | --- | --- |
| Reference/synthetic | “The implementation demonstrates…” | “validated”, “representative”, “global estimate” |
| Internally validated | “The bounded analysis is internally validated for…” | “externally confirmed”, “country ranking” |
| Externally triangulated | “The estimate is consistent with the named independent evidence within…” | Unqualified generalisation beyond the assessed population |
| Community/governance reviewed | “The interpretation was reviewed for the documented population and use…” | Implied endorsement or universal acceptability |
| Release approved | Use only the exact population, period, estimand and uncertainty in the disposition | Any stronger claim than the signed disposition |

Missingness, access constraints, diagnostic capacity and non-estimability must be
visible in the human-readable coverage product. A controlled-data request is an
explicit next evidence action, never evidence that the missing population is
represented.
