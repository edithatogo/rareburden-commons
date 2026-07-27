# Track 010 plan

## Phase 1 — Analysis contracts

- [ ] Define supported estimands, inputs, outputs and invalid operations. `[M-03]`
- [ ] Define distribution and correlation specifications.
- [ ] Define structural scenarios and missingness outputs.
- [ ] Link all inputs and outputs to ledger IDs. `[M-11]`

## Phase 2 — Deterministic engine

- [ ] Implement expected affected-population calculations. `[S-04]`
- [ ] Implement rare-aetiology composition calculations.
- [ ] Implement unit, metric and population compatibility guards.
- [ ] Add lineage-preserving result objects.

## Phase 3 — Uncertainty engine

- [ ] Implement supported probability distributions and sampling. `[M-06]`
- [ ] Record seed, environment and sampling configuration.
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
