# Bounded public-survey R reference crosscheck

Executed 2026-09-06 on macOS arm64. Status: **algorithmic agreement observed**
for the fixed adult NHANES questionnaire ratio and Taylor standard error.
This is agent-executed cross-software evidence, not an independent human review,
clinical validation, completed NCHS reliability assessment, population release
approval or controlled-node activation. The survey module's existing metadata
is unchanged. This sidecar does not establish general disclosure safety.

## Fixed method and checks

The [survey method](track-004-public-survey-method.md) defines the estimand:
known age at least 20, DIQ010=1 numerator, DIQ010 in 1/2/3 denominator,
WTINT2YR interview weights. Borderline is a noncase. Refused, unknown and
missing responses contribute zero to both totals. Missing age is out of domain;
finite fractional ages below one remain unrounded and out of domain.

`scripts/check_public_survey_reference.R` constructs the full positive-weight
DEMO design with `svydesign(ids=~SDMVPSU, strata=~SDMVSTRA,
weights=~WTINT2YR, nest=TRUE)`, without FPC, and applies `svyratio` to domain-case
and domain indicators. Adults are never filtered before design creation.
Two PSUs per stratum are required, including zero-contribution domain PSUs.
The software reference is the primary survey-package documentation for
[design construction](https://r-survey.r-forge.r-project.org/survey/html/svydesign.html),
[ratio estimation](https://r-survey.r-forge.r-project.org/survey/html/svyratio.html)
and [domain estimation](https://r-survey.r-forge.r-project.org/survey/doc/domain.pdf).

Observed checks all passed:

- Invented two-stratum ratio: 0.4, variance 0.1352, SE sqrt(0.1352).
  Weighted residual PSU totals are 0.06, -0.08, 0.18, -0.16;
  variance is 0.14 squared plus 0.34 squared.
- Invented infant-only second PSU in the first stratum: ratio 0.5,
  variance 0.1953125. The out-of-domain PSU is retained.
- Real R ratio and SE agree with the saved Python `nhanes_survey` result.
- Saved Python ratio and SE agree with a fresh current-module API invocation.
- Required columns decoded by `foreign::read.xport` and pandas agree under
  `all.equal(tolerance=1e-14, check.attributes=FALSE)`; this is numerical
  comparison, not a byte-identity claim.
- Pinned raw-XPT and Parquet required-column dataframes are equal in pandas.

Numerical agreement requires each ratio/SE absolute difference to be at most
`1e-12 + 1e-10 * abs(reference)`. No real estimate, count, denominator,
excluded-category total, PSU statistic or participant value is recorded here
or emitted by the script. Only synthetic numerical examples are public.

The R calculation independently decodes XPT and joins by SEQN. Python's minimal
CSV exports are used only for the decoder comparison; they do not supply the
R estimator's records. Agreement between decoders does not prove an IBM/SAS
zero-decoding explanation for fractional infant ages or establish the intended
source representation. The age>=20 estimand is unchanged.

## Exact evidence bindings

Canonical module: `src/rareburden/public_survey.py`, SHA-256
`9171df12381cffde21bb9baf8c4572cfc47b037e06237b74f95845554871683a`.

Saved rehearsal: outside Git at
`/Volumes/PortableSSD/rbd-public-data/node-survey-rehearsal-20260906-b/results.json`,
key `nhanes_survey`; whole-file SHA-256
`2d1fb9fe32177a689793641adecb9cc38d90bd8e642a22d4430bee087898ac21`.
The script verifies its nested canonical output checksum and fixed-method
metadata before comparing. Its source digests bind Parquet, whereas the fresh
API invocation binds raw XPT; verified format-conversion equality connects them.

Inputs are NHANES August 2021–August 2023 DEMO_L and DIQ_L, retrieved
2026-09-06 per the external dataset's `manifest.json`. Source URLs, retrieval
event and format-conversion provenance remain in that manifest. Source-use
conditions remain those in the linked method; this check adds no rights grant.
All inputs reside under
`/Volumes/PortableSSD/rbd-public-data/nhanes-2021-2023-diabetes`.

| File | SHA-256 |
| --- | --- |
| `raw/DEMO_L.xpt` | `ca4374a158b493b8b0163e1388da21d57a18d1b9cecff2aa4e2fa2bec494fe23` |
| `raw/DIQ_L.xpt` | `9535a023673ae869afae19d842d8679e06f6a464606ac15900686b41ef05090f` |
| `data/DEMO_L.parquet` | `24f3623742b1900911bc49b6fcaa0786a9eb3a486dd2d4e86a126514d427ac4f` |
| `data/DIQ_L.parquet` | `72404c82dcd9d9fab2233757e4b4cc97b3b2bc769e25a9d390b1d4fe2eb9242c` |

## Reproduction and environment

From the canonical repository, run:

```sh
/usr/local/bin/Rscript --vanilla scripts/check_public_survey_reference.R
/usr/local/bin/Rscript --vanilla scripts/check_public_survey_reference.R --synthetic-only
```

R 4.3.0; survey 4.4-2 (reported by R as 4.4.2); foreign 0.8-84;
pandas 2.3.3. CRAN supplied the compatible macOS arm64 binary of survey,
built under R 4.3.3, rather than the newer source version 4.5. The package
loaded and both reference calculations executed successfully. The known
package-build warning is suppressed during loading; analysis warnings fail.

Installation succeeded using only `https://cran.r-project.org` and the explicit
private library `/Volumes/PortableSSD/rbd-public-data/r-survey-library`.
Installed dependencies: Rcpp 1.1.0, minqa 1.2.8, numDeriv 2016.8-1.1,
mitools 2.4 and RcppArmadillo 14.6.0-1. Existing R libraries supplied foreign
0.8-84, Matrix 1.5-4, survival 3.5-5 and DBI 1.1.3. No global package install
was performed. These are observed versions, not a portable locked R runtime.

The installation command was:

```r
lib <- "/Volumes/PortableSSD/rbd-public-data/r-survey-library"
dir.create(lib, recursive=TRUE, showWarnings=FALSE)
.libPaths(c(lib, .libPaths()))
options(timeout=60)
install.packages("survey", lib=lib, repos="https://cran.r-project.org",
                 dependencies=NA, type="binary")
```

The runner never installs packages. `PUBLIC_SURVEY_PYTHON` can select a Python
environment with pandas, pyarrow and the module dependencies; its default is
the existing external preliminary-proof virtual environment. It imports the
canonical repository's current source explicitly. This is source-API checking,
not proof of an installed release wheel.

Generated minimal DEMO/DIQ CSVs, expected aggregate comparison values and a
fresh local policy store reside in a uniquely named mode-0700 temporary
directory under `/Volumes/PortableSSD/rbd-public-data`, with umask 0077.
The API applies an aggregate-only minimum-five case/noncase policy before
providing comparison values. The R side repeats that bound. This temporary
store is a local algorithm-check fixture, not a production query authority
or permission to reset a production budget. Temporary files are removed on
normal success or error; interrupted processes may require private cleanup.
Subprocess diagnostics and real-data exception text are withheld. No
row-level or small-cell logs are retained.

## Handoff scope

Only this report and `scripts/check_public_survey_reference.R` belong to this
sidecar. No module edit, Conductor checkbox, runtime projection, commit,
checkout, worktree or release change was made. Main integration should bind
any agreement claim to the tested module digest and rerun after method or
module changes. Statistical-software agreement is limited to this fixed
algorithm, these inputs and the two synthetic cases; clinical meaning,
self-report bias, reliability and accountable review remain separate.
