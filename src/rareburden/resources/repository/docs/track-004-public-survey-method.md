# Bounded NHANES questionnaire survey method

Implementation contract, 2026-09-06. This is an experimental questionnaire-only
analysis of the August 2021–August 2023 release, not a clinical validation,
monogenic-diabetes estimate, controlled-node deployment or release approval.

## Estimand and inputs

Among adults aged at least 20 with a valid DIQ010 response, estimate the
interview-weighted proportion reporting diagnosed diabetes. DIQ010=1 is a case;
1/2/3 form the denominator. Borderline (3) is explicitly a non-case, not an
imputed diagnosis. Refused (7), unknown (9) and missing responses are excluded
from numerator and denominator, without imputation or additional nonresponse
adjustment. Under-20 and missing-age respondents are outside the analysis domain.
Missing age is not imputed and is not interpreted as age zero. The result is
a crude complete-response ratio, not age-standardized or total diabetes burden.

[CDC DIQ_L documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DIQ_L.htm)
specifies interview weights for questionnaire-only analysis and eligibility from
age one. The pregnancy exception in question wording is retained in the meaning
of the self-report; no clinical diagnosis is inferred. A change to laboratory or
examination inputs requires a different method and appropriate weights.

Use SEQN to join DIQ_L to the full DEMO_L design. Eligible demographic records
with known age of at least one must have a questionnaire match; infants and
records with unknown age may lack one. For unknown age, eligibility cannot be
determined: a missing join is not classified as an eligible nonresponse, and a
present response is still excluded from the adult domain. All these records
remain in the positive-weight design. Duplicate, orphan and
ineligible matches fail. Missing DIQ010 within a matched record is an explicit
excluded response, distinct from a missing join. All weights must be finite and
nonnegative; positive weights define the design universe. Zero weights do not
contribute. Design codes, age (0–80, including top coding), required
fields and response codes are validated without echoing participant values.
Only None/NaN is accepted as missing age; nonfinite, out-of-range and fractional
age at or above one still fail. Finite fractional age below one is accepted
without rounding and remains outside DIQ eligibility and the adult domain.
Inspection of the pinned files found fractional values only below one and no
missing ages. Pandas decoding of raw XPT equals the Parquet dataframe, excluding
a Parquet-only conversion difference but not independently validating the SAS
decoder. Missing-age support is defensive, not an explanation for that observed
failure. Missing-age exclusion narrows the estimand to known-age
valid responders; this is an explicit implementation decision, not a CDC
imputation rule or evidence that age missingness is ignorable.
[CDC DEMO_L documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm)
defines WTINT2YR, SDMVSTRA, SDMVPSU and RIDAGEYR. Only this single-cycle,
two-masked-PSU-per-stratum design is supported; singleton strata fail closed.

## Taylor domain variance

For domain indicator d, case indicator y and interview weight w, the ratio is
`p = sum(w*d*y) / D`, where `D = sum(w*d)`. Within each stratum h and PSU j,
sum linearized values `t[h,j] = sum(w*d*(y-p)/D)`. Variance is
`sum_h (t[h,1]-t[h,2])**2`; the exported SE is its square root. This is the
with-replacement Taylor estimator, without a finite-population correction.
All positive-weight demographic PSUs remain, including zero-contribution
out-of-domain PSUs. Filtering to adults before constructing the design is wrong.
[CDC variance tutorial](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx)
recommends Taylor linearization and retaining the full nonzero-weight design for
domain analysis. Common weight rescaling avoids overflow and leaves the method
unchanged; unsupported numerical dynamic range fails closed.

No confidence interval is exported: a naive binomial or normal interval would
not establish reliable survey inference. SE alone is not a completed NCHS
reliability assessment, an external statistical-software agreement check, or a
claim of representative clinical prevalence. Item nonresponse and self-report
bias remain limitations. Hand-calculated invented tests establish algorithmic
behavior, not empirical/clinical validation.

## API and disclosure boundary

`rareburden.public_survey.run_public_survey(demo_rows, diq_rows, *, demo_sha256,
diq_sha256, store, policy_id, policy_sha256, recorded_at)` accepts iterable
mappings and returns a JSON-compatible allowlisted dictionary. The calling
file runner must verify the pinned source bytes before decoding; supplied hashes
alone do not authenticate input. No source rows or actual analysis outputs are
included in Git.

After validation, a fixed query identity reserves the policy-store budget before
any counts or estimates. Only an aggregate-only policy allowing group exports
is accepted. Both unweighted positive-weight domain case and non-case counts
must meet the stored minimum. Otherwise the entire ratio and SE are suppressed;
no counts, denominators, excluded-category totals, identifiers or PSU statistics
are exported. Failure after reservation does not refund or allow a retry. This
is a bounded local release rule, not general disclosure safety, differential
privacy, or proof against privileged store replacement or cross-analysis linkage.
Independent count and survey outputs require joint disclosure review before
release. Tests use invented records only, never real-data disclosure attacks.

The subsequent [R reference crosscheck](track-004-public-survey-reference.md)
establishes fixed-estimator algorithmic agreement against the exact module
digest. It does not complete the reliability assessment or authorize release.

The output reports fixed scope/method/estimand metadata, suppression status,
ratio and SE (or null), explicit absent confidence interval and incomplete
reliability assessment, source/policy/query/receipt digests, and a canonical
JSON SHA-256 calculated before adding `output_sha256`. Caller-owned delivery
and recovery must preserve the committed receipt and exact serialized result.

`eligible_for_local_export` is only a local policy outcome, never publication
approval. Result metadata explicitly records borderline/nonresponse handling,
the pregnancy wording exception, possible proxy responses, crude estimation,
complete-response bias, unverified software agreement and absent population
release approval. The [NCHS data user agreement](https://www.cdc.gov/nchs/policy/data-user-agreement.html)
governs use: statistical reporting/analysis only, no identification or prohibited
linkage and no research assessing NCHS disclosure protections. This implementation
does not certify compliance beyond its bounded documented behavior.
