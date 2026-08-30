# Track 003 synthetic reference acceptance and reproduction

Status: executed, separately reproduced and output-panel reviewed; public Git
delivery is subject to this change's hosted checks and merge. This is the
current acceptance assessment, not an empirical or production release.

The owner explicitly selected Option A after exact-candidate advice. The
[recorded decision](decisions/2026-08-31-track-003-reference-execution.json)
authorizes the package, one clean reproduction, agent output review, reviewed
public-Git retention and completion only if the original criteria pass. The UTC
decision field records when the approval was recorded, not a claimed message
send time. That conditional disposition is applied here; no additional owner
statement, external approval or source permission is invented.

## Exact evidence

- Candidate commit: `36f97490626747b76543f59c44220544978ef874`.
- Candidate tree: `8e70545e1ffa4eb202ad444e3d68d158ce184f82`.
- Manifest SHA-256: `b6f50a8b8b10bddceafd16ddaeee17e77fb6eefb8fbfd724cf747378b5a99911`.
- Decision SHA-256: `16ff18f14b6995139a3baca7b3ec90906e3cad128959ce176e7dbc33b0d3a4d2`.
- Execution and reproduction receipts: `manifests/demonstrators/track-003-reference-execution-2026-08-31.json` in the full repository checkout.
- [Output-panel findings](reviews/track-003-reference-output-panel-2026-08-31.yml).
- Full-checkout output directory: `results/track-003-reference-2026-08-31/`,
  containing `reference-report.md`, `reference-results.json` and
  `reference-tables.csv`. These files are not in the installed documentation projection.

Both runs used separate clean detached checkouts, separate frozen Python 3.13.13
virtual environments and the same approved inputs/seed/10,000 iterations. All
three SHA-256 values matched exactly. The primary directory was moved intact
into the repository; the separate reproduction is retained locally. The public
receipt preserves both printed run receipts. This is same-host owner-operated
reproduction, not independent validation. No third analytical run was performed.

The report, CSV and JSON are unchanged reviewed bytes. Historical in-memory and
pending status labels in bound code/manifests are not current authorization
claims: the separate decision and execution receipt establish the actual events.
The historical single-output assurance receipt is not rewritten or extended.

## Original acceptance mapping

| Criterion | Evidence and disposition |
|---|---|
| 1. Versioned entities and denominator | RBC-P002 bounded registration and synthetic hierarchy remain versioned. The manifest-bound input bundle defines fictional D/E/G states, ages 0–100, all sexes, geography, year and denominator. Clinical gene/phenotype freeze remains excluded. Pass for the original permitted synthetic reference. |
| 2. Parameter provenance, quality and transport | Eighteen explicitly invented parameter records have content-addressed quality and transport records in `examples/demonstrators/track-003-reference-inputs.json`. Scenario contexts bind parameter IDs and hypothetical transfer assumptions; no empirical promotion. Pass. |
| 3. Reproducible primary and sensitivities | Twelve scenarios executed with deterministic plug-ins and seeded summaries. Separate clean execution reproduced every byte of the three-file package. Receipts, exact source/environment manifest and instructions are retained. Pass. |
| 4. Population-state distinctions | Within-diabetes case and detection probabilities, modelled total/detected/undetected people and unavailable denominator are distinct. Observed diagnoses and total-population prevalence are unavailable, not inferred. Pass. |
| 5. Compatible outcomes and costs | Full-year complication/cost and detected-case treatment scenarios are explicitly invented, with eligibility, units, constant fictional price year and non-causal interpretation. Delay is a conditional historical assumption. Pass as labelled scenarios. |
| 6. Uncertainty and structure | Report and every CSV row state invented conditional uncertainty, unquantified fixed design, units and conditioning. Age, applicability, selection, penetrance, denominator and shared/independent stratum assumptions are explicit. Pass. |
| 7. Scientific/engineering challenge and owner disposition | Exact implementation and output reviews pass. Option A was explicitly selected after candidate advice; its completion/public-retention conditions are applied to this evidence, subject to hosted checks. No independent authority is claimed. Pass. |
| 8. Simulated harm challenge | Actual report/table/JSON reviewed; no blocking language or framing findings. Actual community participation, representation, consent, endorsement and independent review remain false. Pass. |

## Evidence-family and comparison adjudication

The evidence-ledger task is complete as an assessment and inventory, not an
assertion that usable empirical parameters exist in every family. Aetiologic
fractions are assessed by age, phenotype, ancestry and setting; the qualified
records remain sensitivity-only or unsuitable. Diagnosis-delay and treatment
aggregates are descriptive and source-located. Complication and service-use
families have explicit held/gap dispositions. The licensed adult diagnostic-yield
record is not general service-use intensity. These gaps remain open in the
bound gap register; no source is promoted by this closeout.

Scientific, engineering and harm advice supports accepting the documented
applicability/noncomparability assessment under Option A. The independent-cohort
comparison task is satisfied by that explicit applicability assessment, **not**
empirical agreement testing: selected clinical populations, genetic-testing
duration and referral yields do not validate fictional population probabilities,
delay definitions, complications or prices. No compatible empirical comparator
is asserted. Synthetic self-agreement is only numerical reproduction. This
disposition does not remove an original acceptance criterion or waive a source
right; it applies the specification's permitted synthetic/scenario scope.

Transport parameters are defined as invented sensitivity assumptions, not
calibrated empirical ranges. Model eligibility is an ancestry-applicability
stress test, not a biological ancestry coefficient. Unknown/uncovered burden is
unavailable, not zero. Public retention consists of original synthetic outputs,
code and attributed metadata; no new empirical source bytes or participant rows
are included.

## Verification and reproduction instructions

For non-executing verification in a full repository checkout:

```sh
uv sync --frozen --extra dev --python 3.13
uv run python -m scripts.check_track003_reference_closeout --root .
```

This verifies exact decision, candidate files, retained output hashes, both
receipts and report/CSV rendering from existing summaries without simulation.
It works without Git history or network after dependencies are installed.
The complete public reproducibility package is the repository checkout/archive,
not the three output files alone. Inputs, code and `uv.lock` are bound by the
candidate manifest; outputs are outside the installed wheel's runtime projection.

The approved two runs followed the bound
[execution plan](track-003-reference-package-plan-2026-08-30.md): create separate
clean detached worktrees at the exact commit, install frozen Python 3.13 dev
environments and invoke `python -m scripts.track003_reference_package` with the
same decision and distinct previously absent output directories. Check the
three printed digests against the retained receipt. Do not run a new retained
analysis under the already-consumed two-copy authorization; any further run
requires its own applicable disposition. Routine validators do not re-execute it.

Local preflight passed all gates and 1,595 tests. Closeout adds mutation-tested
offline integrity checks; its full validation and hosted CI must pass before
merge. No production tag, deployment, empirical activation, clinical validity,
controlled-data permission or external/community authority is established.
