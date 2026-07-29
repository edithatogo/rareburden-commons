# Track 010 plan

## Phase 1 — Analysis contracts

- [x] Define supported estimands, inputs, outputs and invalid operations. `[M-03]` Evidence: synthetic reference contract in `docs/burden-engine-010-reference.md` and existing burden tests.
- [x] Define supported distribution specification (seeded beta fraction propagation); correlation specifications remain out of scope pending contract review.
- [ ] Define structural scenarios and missingness outputs.
- [ ] Link all inputs and outputs to ledger IDs. `[M-11]`

## Phase 2 — Deterministic engine

- [x] Implement expected affected-population calculations. `[S-04]` Evidence: `expected_affected_population` and tests.
- [x] Implement rare-aetiology composition calculations. Evidence: `rare_aetiology_cases` and tests.
- [x] Implement unit, metric and population compatibility guards. Evidence: fail-closed burden tests.
- [ ] Add lineage-preserving result objects.

## Phase 3 — Uncertainty engine

- [x] Implement supported probability distributions and sampling. `[M-06]` Evidence: seeded beta propagation and tests.
- [x] Record seed and sampling configuration. Evidence: `SimulationSummary` includes seed, draws and unit.
- [ ] Implement correlation and structural-scenario handling.
- [ ] Add uncertainty decomposition and sensitivity outputs.

## Phase 4 — Assurance

- [ ] Add unit, property, golden, convergence and numerical-stability tests.
- [ ] Add negative tests for incompatible DALY/cost shortcuts.
- [ ] Benchmark reference workloads.
- [ ] Run independent scientific-software review.

## Phase 5 — Release

- [ ] Produce reproducible public/synthetic reference report.
- [ ] Document API/CLI and interpretation limits.
- [ ] Freeze alpha interfaces required by Track 003.
- [ ] Record review and residual risks.

## Dependency review — 2026-07-27

- [x] Record that Track 010 cannot activate until Track 009 is complete. Evidence: `17b5c69`.
- [x] Add non-binding burden engine contract v0.1.0 draft to the specification; activation and contract freeze remain blocked.
