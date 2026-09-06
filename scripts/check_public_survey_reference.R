#!/usr/local/bin/Rscript
# Local algorithmic sidecar; never print real estimates, cells, or source rows.
# Usage: Rscript --vanilla scripts/check_public_survey_reference.R [--synthetic-only]
options(warn = 2, survey.lonely.psu = "fail")
lib <- "/Volumes/PortableSSD/rbd-public-data/r-survey-library"
.libPaths(c(lib, .libPaths()))
suppressWarnings(suppressPackageStartupMessages(library(survey)))

ratio <- function(d) {
  d <- d[d$WTINT2YR > 0, , drop = FALSE]
  stopifnot(nrow(d) > 0, all(is.finite(d$WTINT2YR)))
  psus <- split(d$SDMVPSU, d$SDMVSTRA)
  stopifnot(all(vapply(psus, function(x) setequal(unique(x), c(1, 2)), TRUE)))
  d$denominator <- as.numeric(!is.na(d$RIDAGEYR) & d$RIDAGEYR >= 20 &
                              d$DIQ010 %in% c(1, 2, 3))
  d$numerator <- as.numeric(d$denominator == 1 & d$DIQ010 %in% 1)
  stopifnot(sum(d$denominator) > 0)
  # No adult/response filtering before design creation; no FPC.
  design <- svydesign(ids = ~SDMVPSU, strata = ~SDMVSTRA,
                      weights = ~WTINT2YR, nest = TRUE, data = d)
  result <- svyratio(~numerator, ~denominator, design)
  c(estimate = unname(coef(result)[1]), se = unname(SE(result)[1]))
}
close_enough <- function(a, b) {
  all(is.finite(a)) && all(is.finite(b)) &&
    all(abs(a - b) <= 1e-12 + 1e-10 * abs(b))
}
synthetic <- data.frame(SDMVSTRA = c(1, 1, 2, 2), SDMVPSU = c(1, 2, 1, 2),
                        WTINT2YR = 1:4, RIDAGEYR = 20, DIQ010 = c(1, 2, 1, 3))
stopifnot(close_enough(ratio(synthetic), c(0.4, sqrt(0.1352))))
# A zero-contribution PSU remains in the full design.
domain_fixture <- synthetic
domain_fixture$RIDAGEYR[2] <- 0.5
domain_fixture$DIQ010[2] <- NA_real_
stopifnot(close_enough(ratio(domain_fixture), c(0.5, sqrt(0.1953125))))
cat("synthetic_hand_calculation=PASS; synthetic_zero_domain_psu=PASS\n")
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 0 || identical(args, "--synthetic-only"))
if (identical(args, "--synthetic-only")) quit(status = 0)

repo <- "/Volumes/PortableSSD/GitHub/rareburden-commons-single-owner-governance"
root <- "/Volumes/PortableSSD/rbd-public-data"
python <- Sys.getenv("PUBLIC_SURVEY_PYTHON", file.path(root,
  "public-node-install-20260906/preliminary-proof/venv/bin/python"))
stopifnot(file.exists(python), !startsWith(normalizePath(root), paste0(repo, "/")))
old_umask <- Sys.umask("0077")
scratch <- tempfile("survey-reference-", tmpdir = root)
dir.create(scratch, mode = "0700")
# Generated interchange and policy receipt stay private and are removed on exit.
stage <- "python_preparation"
main <- function() {
  on.exit(unlink(scratch, recursive = TRUE), add = TRUE)
  on.exit(Sys.umask(old_umask), add = TRUE)
  code <- r"(
import csv, hashlib, importlib, json, math, os, pathlib, sys
os.umask(0o077)
repo, out = map(pathlib.Path, sys.argv[1:3])
sys.path.insert(0, str(repo / 'src'))
import pandas as pd
from rareburden.public_survey import run_public_survey
from rareburden.node_policy_store import DurableNodePolicyStore
module = importlib.import_module('rareburden.public_survey')
source_hash = hashlib.sha256(pathlib.Path(module.__file__).read_bytes()).hexdigest()
raw = pathlib.Path('/Volumes/PortableSSD/rbd-public-data/nhanes-2021-2023-diabetes/raw')
pins = {'DEMO_L': 'ca4374a158b493b8b0163e1388da21d57a18d1b9cecff2aa4e2fa2bec494fe23',
        'DIQ_L': '9535a023673ae869afae19d842d8679e06f6a464606ac15900686b41ef05090f'}
frames = {}
for name, columns in [('DEMO_L', ['SEQN','RIDAGEYR','WTINT2YR','SDMVSTRA','SDMVPSU']),
                      ('DIQ_L', ['SEQN','DIQ010'])]:
    path = raw / (name + '.xpt')
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pins[name]
    frames[name] = pd.read_sas(path, format='xport')[columns]
    frames[name].to_csv(out / (name + '.csv'), index=False)
with DurableNodePolicyStore(out / 'policy.sqlite3') as store:
    receipt = store.register_policy({
        'schema_version':'0.1.0', 'policy_id':'survey-reference-local',
        'minimum_cell_count':5, 'max_queries_per_overlap_group':1,
        'allowed_dimension_fields':['group'], 'participant_fields':['person_id'],
        'export_mode':'aggregate_only'}, recorded_at='2026-09-06T00:00:00Z')
    result = run_public_survey(frames['DEMO_L'].to_dict('records'),
        frames['DIQ_L'].to_dict('records'), demo_sha256=pins['DEMO_L'],
        diq_sha256=pins['DIQ_L'], store=store, policy_id=receipt.policy_id,
        policy_sha256=receipt.content_sha256, recorded_at='2026-09-06T00:01:00Z')
    assert result['status'] == 'eligible_for_local_export'
assert hashlib.sha256(pathlib.Path(module.__file__).read_bytes()).hexdigest() == source_hash
artifact = pathlib.Path('/Volumes/PortableSSD/rbd-public-data/node-survey-rehearsal-20260906-b/results.json')
artifact_bytes = artifact.read_bytes()
saved = json.loads(artifact_bytes)['nhanes_survey']
saved_unsigned = {k:v for k,v in saved.items() if k != 'output_sha256'}
assert hashlib.sha256(json.dumps(saved_unsigned, sort_keys=True,
    separators=(',', ':'), allow_nan=False).encode()).hexdigest() == saved['output_sha256']
parquet_pins = {'DEMO_L':'24f3623742b1900911bc49b6fcaa0786a9eb3a486dd2d4e86a126514d427ac4f',
                'DIQ_L':'72404c82dcd9d9fab2233757e4b4cc97b3b2bc769e25a9d390b1d4fe2eb9242c'}
for name, field in [('DEMO_L','demo_sha256'), ('DIQ_L','diq_sha256')]:
    path = raw.parent / 'data' / (name + '.parquet')
    assert hashlib.sha256(path.read_bytes()).hexdigest() == parquet_pins[name]
    assert saved[field] == parquet_pins[name]
    assert frames[name].equals(pd.read_parquet(path)[list(frames[name].columns)])
for field in ['status','estimand','weight','variance_method',
              'case_definition','denominator_codes','age_handling']:
    assert saved[field] == result[field]
for field in ['estimate','standard_error']:
    assert math.isfinite(saved[field])
    assert abs(saved[field]-result[field]) <= 1e-12 + 1e-10*abs(result[field])
with (out / 'expected.csv').open('w') as f:
    writer = csv.writer(f)
    writer.writerow(['estimate','se','module_sha256','pandas_version','artifact_sha256'])
    writer.writerow([saved['estimate'],saved['standard_error'],source_hash,pd.__version__,
                     hashlib.sha256(artifact_bytes).hexdigest()])
)"
  # Discard subprocess diagnostics: even exceptional decoder errors must not leak rows.
  status <- system2(python, c("-c", shQuote(code), shQuote(repo), shQuote(scratch)),
                    stdout = FALSE, stderr = FALSE)
  if (status != 0) stop("private Python preparation/module comparison failed", call. = FALSE)
  stage <<- "foreign_decode"
  pandas_demo <- read.csv(file.path(scratch, "DEMO_L.csv"))
  pandas_diq <- read.csv(file.path(scratch, "DIQ_L.csv"))
  raw <- file.path(root, "nhanes-2021-2023-diabetes/raw")
  demo <- foreign::read.xport(file.path(raw, "DEMO_L.xpt"))[names(pandas_demo)]
  diq <- foreign::read.xport(file.path(raw, "DIQ_L.xpt"))[names(pandas_diq)]
  # Compare only required fields, without printing all.equal diagnostics or rows.
  decoder_equal <- isTRUE(all.equal(demo, pandas_demo, tolerance = 1e-14,
                                    check.attributes = FALSE)) &&
    isTRUE(all.equal(diq, pandas_diq, tolerance = 1e-14, check.attributes = FALSE))
  stage <<- "join_and_domain"
  # Decoder differences are reported separately; the fixed-estimand check remains decisive.
  stopifnot(!anyDuplicated(demo$SEQN), !anyDuplicated(diq$SEQN),
            all(diq$SEQN %in% demo$SEQN))
  matched <- match(demo$SEQN, diq$SEQN)
  stopifnot(all(!is.na(matched[!is.na(demo$RIDAGEYR) & demo$RIDAGEYR >= 1])),
            all(is.na(matched[!is.na(demo$RIDAGEYR) & demo$RIDAGEYR < 1])))
  demo$DIQ010 <- diq$DIQ010[matched]
  valid <- demo$WTINT2YR > 0 & !is.na(demo$RIDAGEYR) & demo$RIDAGEYR >= 20 &
    demo$DIQ010 %in% c(1, 2, 3)
  stopifnot(sum(valid & demo$DIQ010 %in% 1) >= 5,
            sum(valid & demo$DIQ010 %in% c(2, 3)) >= 5)
  actual <- ratio(demo)
  stage <<- "numerical_comparison"
  expected <- read.csv(file.path(scratch, "expected.csv"), colClasses =
                         c("numeric", "numeric", "character", "character", "character"))
  stopifnot(close_enough(actual, c(expected$estimate, expected$se)))
  cat("real_fixed_estimand_ratio_and_taylor_se=PASS\n")
  cat("saved_python_artifact_vs_current_module=PASS\n")
  cat("foreign_vs_pandas_required_columns_equal=", decoder_equal, "\n", sep = "")
  cat("module_sha256=", expected$module_sha256, "\n", sep = "")
  cat("artifact_sha256=", expected$artifact_sha256, "\n", sep = "")
  cat("pandas=", expected$pandas_version, "; survey=",
      as.character(packageVersion("survey")), "; foreign=",
      as.character(packageVersion("foreign")), "; ", R.version.string, "\n", sep = "")
}
# Never print condition text from real-data processing.
tryCatch(main(), error = function(e) {
  cat("real_fixed_estimand_crosscheck=FAIL; stage=", stage,
      " (diagnostics withheld)\n", sep = "")
  quit(status = 1)
})
