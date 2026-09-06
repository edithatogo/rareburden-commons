# Track 004 real-public-data counting tranche

Purpose: implement the owner's requested UCI/NHANES next step without relabelling
real records as synthetic. Status: experimental descriptive execution, not a
production release or extension of the historical synthetic closeout approval.

## Inputs and rights

The owner selected both datasets and authorised public Hugging Face publication
where source rights permit. The exact snapshots used are:

- [UCI mirror](https://huggingface.co/datasets/edithatogo/uci-diabetes-130-us-hospitals/tree/fcaac2a2bc2a5b3c4526bf36a9d59892b3b0633a),
  `data/encounters.parquet`, SHA-256
  `cf435350273822ed4a3193e8dfd22e38bbf264839073c353cf2dda2b1fab1cb9`.
  Clore, Cios, DeShazo and Strack (2014), DOI 10.24432/C5230J, CC BY 4.0.
- [NHANES mirror](https://huggingface.co/datasets/edithatogo/nhanes-2021-2023-diabetes/tree/1b5a370cb2e3bca31b9559238817c4eb21b00070),
  `data/DIQ_L.parquet`, SHA-256
  `72404c82dcd9d9fab2233757e4b4cc97b3b2bc769e25a9d390b1d4fe2eb9242c`.
  CDC/NCHS NHANES August 2021–August 2023 public-use questionnaire, published
  September 2024. The source mirror retains the XPT originals, conversion
  provenance and NCHS statistical-use restrictions. No re-identification or
  research assessing NHANES disclosure methods is performed.

Mirrors were acquired and rights-screened on 2026-09-06. Their cards and manifests
retain source URLs, raw hashes, licence references and format-conversion details.
Data remain outside this code repository. This tranche uses neither DEMO_L nor
weights and does not claim population inference, genetic classification or
monogenic-diabetes validity.

## Implemented contract

`rareburden.public_node` is additive; existing synthetic runners are unchanged.
UCI counts encounters by recorded readmission category, preserving repeated
encounters for the same person. It rejects duplicate encounter IDs rather than
silently deciding how to deduplicate them. NHANES counts questionnaire responses
without weights, keeping borderline, unknown, refusal and missing distinct.
No arbitrary filters, linkage, user-selected categories or population estimates
are supported. Counts describe the source sample only.

The file runner verifies exact Parquet bytes before parsing. The library API
accepts an operator-supplied digest; it cannot authenticate arbitrary caller
records. Input preflight freezes the selected labels before reservation. Fixed
dataset analysis/overlap identities prevent changed data from implicitly buying
a new budget. The store verifies the expected policy hash transactionally and
commits the value-free receipt before counting. Post-commit failures consume the
reservation; uncertain commits stop with no automatic retry or refund.

The output uses a fixed, public category order, minimum-cell suppression and no
overall total. These controls are not a guarantee against inference from public
source totals or other releases. Local owner policy is not external custodian
authority. Privileged file replacement, malicious code alteration, institutional
deployment, production recovery and signed delivery remain outside this tranche.

## Execution and verification

Two local invocations succeeded on macOS ARM64, with the second executed under
`sandbox-exec -p '(version 1)(allow default)(deny network*)'`.
Both used the existing conversion environment: pandas 2.3.3, pyarrow 21.0.0 and
NumPy 2.5.2. This is network-denied execution, not fresh disconnected installation.
Results and SQLite stores were retained outside Git in distinct, explicitly
requested rehearsal directories. A new rehearsal store is not permission to
reset any production store.

The reproducible projection
`map_values({dataset,unit,category_order,rows,source_sha256,policy_sha256})`,
serialized by `jq -S`, has SHA-256
`95e1e486200fff33852be3cf97a6de5256b2a3b1231c89217d7b5791d64b810f`
in both runs. Timestamp-dependent receipt chains and complete output hashes are
not claimed byte-identical. The store verified one policy and two reservations.

From the checkout, with pandas/pyarrow available and source files already staged:

```sh
PYTHONPATH=src:. python scripts/run_public_node_counts.py \
  --source-root /path/to/public-snapshots --output /new/local/rehearsal-directory
```

The output directory must not exist. Preserve it on failure for inspection; do
not retry by replacing its store. `results.json` is written only after both
computations succeed. File delivery is not yet an atomic, durable publication
protocol; an interrupted write is not a successful result receipt.

Fourteen invented-fixture tests cover counting units, missingness, invalid codes,
duplicate IDs, hash mismatch, restart replay and consumed budget after export
failure. No real NHANES data are used for adversarial tests.

## Advisory review

A separate read-only engineering agent returned pass with limits for the three
new code/test files: frozen input, reservation-before-counting, duplicate-unit
checks and pinned-file provenance were inspected. It did not independently test
the imported store or export validator. No blocking defect was identified in
that bounded static review. This is agent advice, not owner acceptance.

Residual observations: UCI digit-string keys with different leading zeros remain
distinct; library callers can assert an unrelated source digest; the reservation
itself does not authenticate source provenance; interrupted output writes may
leave an incomplete file. Pinned source bytes constrain the first two risks in
the supplied runner. No production identity, provenance or delivery guarantee
is inferred. Full repository validation passed 2,140 tests; focused lint and
strict typing of the new module passed.

## Remaining work

Population estimates need a separate survey-aware analysis contract, DEMO_L
joining and weight/design/variance validation. Also pending: a complete locked
real-data runtime, clean installed-package proof, atomic result delivery and
recovery protocol, broader role-separated review, exact-candidate owner acceptance
and release. The earlier Complete metadata refers to its historical bounded
synthetic scope, not completion of this real-data follow-up.
