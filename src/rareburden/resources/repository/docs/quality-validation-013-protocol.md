# Track 013 bounded assurance protocol

**Status:** adopted for synthetic and metadata-only repository assurance.

## Validation types

- Internal validation checks schema, invariant, lineage, missingness,
  suppression and deterministic-reproduction behavior.
- External validation compares an exact candidate with attributable empirical
  evidence only when such evidence is lawfully available.
- Predictive validation remains `not_assessed` without held-out empirical data.
- Face-validity advice is supplied by role-separated agents and decided by the
  owner; it is not lived-experience testimony or independent human review.

## Calibration and model criticism

Synthetic calibration passes only when deterministic fixtures reproduce within
their registered numerical tolerance and uncertainty closure checks pass.
Empirical calibration remains `not_assessed` until a prerequisite analysis and
comparison source are both active. Model criticism must inspect missingness,
suppression, structural assumptions, uncertainty concentration, unsupported
transport and claim maturity. A failed invariant, unresolved critical finding,
or attempted empirical overclaim blocks the affected output.

## Release-language rules

- `synthetic`: describe contract behavior only.
- `metadata_only`: describe availability, access and gaps; never sufficiency.
- `empirical_bounded`: describe the named population, geography, release and
  uncertainty only after exact evidence binding and owner disposition.
- `representative`: prohibited without scope-matched representation evidence.
- `global`: prohibited unless the roadmap representation conditions are met.

Missing, unavailable, suppressed and `not_assessed` states must remain visible
and must never be rendered as zero. A third-party receipt is required only
before activating the specific data, permission, representation or authority
to which it relates.
