# Track 013 assurance reference

The repository’s assurance layer is deliberately rule-based and fail-closed:

- evidence assessments use domain judgements rather than an opaque composite score;
- transportability records identify target population, use, uncertainty inflation
  and unresolved questions;
- quality dispositions block primary or target-population use when the relevant
  judgement is not adequate;
- the gap-map generator reports access/readiness capability and keeps
  `sufficiency: not_assessed` until empirical review exists;
- the GATHER checklist requires evidence or an explicit not-satisfied rationale.

These controls are suitable for synthetic and metadata-only assurance. They do
not establish empirical calibration, independent reproduction, equity adequacy,
or patient/community acceptability. Those remain Track 013 release gates.
