# Track 010 plan

> Repository-owned review uses the subagent panel under ADR-0008; scientific, patient/community and engineering dispositions remain separate.

## Phase 1 — Analysis contracts

- [x] Define supported estimands, inputs, outputs and invalid operations. `[M-03]` Evidence: synthetic reference contract in `docs/burden-engine-010-reference.md` and existing burden tests.
- [x] Define supported distribution specification (seeded beta fraction propagation); correlation specifications remain out of scope pending contract review.
- [x] Define bounded structural-scenario and fail-closed missingness outputs. Evidence: `rareburden.burden_assurance`, focused reproducibility/negative tests and `docs/burden-engine-010-reference.md`; scientific approval remains open.
- [x] Link all inputs and outputs to ledger IDs. `[M-11]` Evidence: analysis and scenario outputs retain ledger ID, parameter IDs, parameter fingerprints and content-derived result IDs; empirical ledger activation remains Track 009-gated.

## Phase 2 — Deterministic engine

- [x] Implement expected affected-population calculations. `[S-04]` Evidence: `expected_affected_population` and tests.
- [x] Implement rare-aetiology composition calculations. Evidence: `rare_aetiology_cases` and tests.
- [x] Implement unit, metric and population compatibility guards. Evidence: fail-closed burden tests.
- [x] Add lineage-preserving result objects. Evidence: analysis results and structural-scenario records retain ledger ID, parameter IDs, parameter fingerprints and result IDs with schema-valid base-result coverage.

## Phase 3 — Uncertainty engine

- [x] Implement supported probability distributions and sampling. `[M-06]` Evidence: seeded beta propagation and tests.
- [x] Record seed and sampling configuration. Evidence: `SimulationSummary` includes seed, draws and unit.
- [x] Implement bounded structural-scenario handling and reject unsupported correlation. Evidence: `run_structural_scenarios`, invariant/estimability tests and the explicit `simulate_product` dependence error; no correlated model is claimed.
- [x] Add uncertainty decomposition and bounded structural-sensitivity outputs. Evidence: `decompose_independent_product`, `run_structural_scenarios`, schema validation and focused deterministic/closure tests; correlated-input decomposition remains unsupported pending scientific approval.

## Phase 4 — Assurance

- [x] Add unit, property, golden, convergence and numerical-stability tests. Evidence: `tests/test_burden_numerical_assurance.py`, existing burden/ledger suites and explicit overflow/negative-product rejection.
- [x] Add negative tests for incompatible DALY/cost shortcuts. Evidence: `tests/test_burden.py` and `tests/test_quality_edges.py`.
- [x] Benchmark the bounded synthetic reference workload. Evidence: `scripts/check_burden_benchmark.py`, its fail-closed tests and the `make burden-benchmark` release gate; timing is an engineering guard, not scientific validation.
- [ ] Run independent scientific-software review.

## Phase 5 — Release

- [x] Produce reproducible public/synthetic reference report. Evidence: `docs/burden-engine-010-reference.md`.
- [x] Document API/CLI and interpretation limits. Evidence: reference report and `estimate-cases` CLI contract.
- [ ] Freeze alpha interfaces required by Track 003.
- [x] Record repository review and residual risks. Evidence: `review.md`; external scientific-software, patient/community and engineering dispositions remain pending.

## Dependency review — 2026-07-27

- [x] Record that Track 010 cannot activate until Track 009 is complete. Evidence: `17b5c69`.
- [x] Add non-binding burden engine contract v0.1.0 draft to the specification; activation and contract freeze remain blocked.

## Blocker resolution — 2026-07-29

- [x] Record local resolution and residual gates for estimands, uncertainty, prohibited shortcuts, unsupported correlation/scenario behaviour and Track 009 dependency. Evidence: blocker resolution matrix in `review.md`.

## Preparation refresh — 2026-08-01

- [x] Prepare the burden-engine review packet with estimand, uncertainty,
  dependence, structural-scenario, safety-boundary and alpha-freeze decisions.
  Evidence: `docs/track-010-engine-review-packet.md`; Track 009 and external
  scientific/engineering/patient-community review remain open.

## Preparation refresh — 2026-08-02

- [x] Add a focused contract test proving the synthetic reference remains
  explicitly bounded and non-empirical. Evidence:
  `tests/test_downstream_track_contracts.py`; scientific and Track 009 gates
  remain open.
