# Track 010 plan

> Repository-owned review uses the subagent panel under ADR-0008; scientific, patient/community and engineering dispositions remain separate.

## Phase 1 — Analysis contracts

- [x] Reconcile the bounded engine against the exact merged Track 009
  source-release binding set. The executable receipt validates every referenced
  source release, permits `synthetic_assurance` only, and records both empirical
  activation and contract freeze as false. Evidence:
  `manifests/burden/track-010-bounded-synthetic-receipt-2026-08-16.json`.

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
- [ ] Run role-separated scientific-software agent-panel review and owner disposition.
  The repository-owned bounded synthetic quality disposition is prepared, but
  it is not an agent-panel or clinical disposition.

## Phase 5 — Release

- [x] Produce reproducible public/synthetic reference report. Evidence: `docs/burden-engine-010-reference.md`.
- [x] Document API/CLI and interpretation limits. Evidence: reference report and `estimate-cases` CLI contract.
- [ ] Freeze alpha interfaces required by Track 003.
- [x] Record repository review and residual risks. Evidence: `review.md`; external scientific-software, patient/community and engineering dispositions remain pending.

## Dependency review — 2026-07-27

- [x] Record that Track 010 cannot activate until Track 009 is complete. Evidence: `17b5c69`.
- [x] Add non-binding burden engine contract v0.1.0 draft to the specification; activation and contract freeze remain blocked.
- [x] Prepare the Track 003 interface handoff without freezing it. Evidence:
  `docs/track-010-engine-review-packet.md` records the draft contract,
  lineage/result requirements and explicit activation rule; alpha freeze remains
  dependent on Track 009 and external review.

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

## Track 009 reconciliation — 2026-08-16

- [x] Replace the stale incomplete-Track-009 dependency statement with an exact
  binding to the merged Track 009 manifest and its immutable source evidence.
- [x] Add a deterministic renderer and committed receipt for the existing
  synthetic analysis, including the Track 009 binding digest, quality
  disposition ID, parameter fingerprints, deterministic seed and explicit
  non-activation state.
- [x] Add negative tests that reject primary use, empirical activation and a
  frozen v0.4 contract. No empirical source, semantic, clinical, policy or
  production activation follows from this reconciliation.

## Option B preparation control — 2026-08-20

- [x] Enforce reversible synthetic engine preparation without allowing Track
  010 to activate before Track 009 completes or an alpha interface to be
  represented as frozen. Evidence:
  `docs/downstream-bounded-preparation-plan-2026-08-03.yml`,
  `scripts/check_downstream_preparation.py` and focused fail-closed tests.
  Scientific-software, clinical/community and alpha-freeze gates remain open.

## Review fixes — 2026-08-20

- [x] Compile immutable distribution samplers once per simulation and
  decomposition run, preserve the versioned random stream with a golden output
  digest, and measure the CPU-only benchmark using process CPU time rather than
  contention-sensitive wall time. The 15-second limit is unchanged; the receipt
  explicitly disclaims end-to-end wall latency. External scientific-software
  review and alpha-interface freeze remain open.

## Alpha-freeze readiness control — 2026-08-21

- [x] Encode and machine-enforce the Track 009 dependency, independent and
  accountable review receipts, exact engine/ledger/Track 003 interface hashes,
  compatibility/migration evidence and alpha-freeze decision required for
  closure. Evidence: `docs/track-010-alpha-freeze-readiness-2026-08-21.yml`,
  `scripts/check_track_010_alpha_freeze_readiness.py` and negative tests.
  Both parent blocking tasks remain open.
- [x] Reconcile the exact synthetic-only Track 009 contract freeze with Track
  010's older whole-track-completion prerequisite and prepare three owner
  options. Evidence:
  `docs/decisions/2026-08-21-track-010-upstream-dependency-disposition.yml`
  and `docs/track-010-alpha-freeze-readiness-2026-08-21.yml`. The recommended
  narrow exception permits exact synthetic alpha-candidate preparation only;
  the owner selected it without freezing an interface, activating empirical or
  production use, or supplying accountable review.
- [x] Prepare the exact synthetic alpha candidate with engine, frozen-ledger,
  Track 003 interface, compatibility/migration, benchmark/reproducibility and
  repeated challenge bindings. Evidence:
  `manifests/burden/track-010-alpha-candidate-2026-08-21.json` and its bound
  artifacts plus `docs/track-010-alpha-candidate-challenge-2026-08-21.yml`.
  Empirical parameter count is zero; all approval, interface-freeze, Track 003
  activation, production activation and Track completion claims remain false.
