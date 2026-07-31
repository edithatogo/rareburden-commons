# Track 010 dependency review — Public burden engine and uncertainty framework

**Review date:** 2026-07-27  
**Decision:** Blocked pending Track 009

### Review rerun — 2026-07-29

Repository review result: **Pass with dependency and scientific gates**. The
synthetic reference report, deterministic estimands, seeded uncertainty summary,
unit guards and prohibited-operation tests are consistent with the plan. The
full project validation gate passes. Track 010 remains blocked because Track
009 is incomplete and no scientific, engineering or patient/community review
has approved an alpha interface.

## Findings

- Track 009 is blocked by the incomplete source-acquisition and semantic contracts.
- No approved Track 010 estimand contract, track-scoped alpha interface or release assurance package has been completed; reusable model primitives and tests are preparatory only.
- Scientific, engineering and patient/community review gates remain required.

Repository-owned alpha work is now documented in
`docs/burden-engine-010-reference.md`: supported deterministic estimands,
seeded beta uncertainty propagation, unit guards and prohibited DALY/cost
shortcuts are covered by existing focused tests. This is synthetic assurance
only and does not activate Track 010 or freeze a Track 003 interface.

### Preparatory assurance rerun — 2026-07-31

The bounded synthetic engine now emits explicit non-estimability records without
imputation and can execute two to twenty named structural scenarios while
holding the analysis identity, estimand, output unit and intended use invariant.
Each scenario retains its analysis-result ID, ledger ID, parameter IDs and
parameter fingerprints, and reports its mean change from the declared baseline.
Reproducibility and fail-closed missing-input/invariant tests pass.

This does not approve the scenario set, establish a dependence model, complete
correlated-input uncertainty decomposition or freeze an alpha interface. The
existing independent-product moment decomposition is schema-validated and now
paired with a bounded reference-workload benchmark gate.

### Blocker resolution matrix — 2026-07-29

| Blocker | Repository action | Status | Remaining gate |
|---|---|---|---|
| Undefined alpha estimands | Synthetic reference defines affected-population and rare-aetiology cases, units and invalid operations | resolved locally | Scientific/statistical approval |
| Unbounded uncertainty behaviour | Seeded propagation records seed/draws/unit; independent-product decomposition and structural sensitivities have deterministic coverage | resolved locally for independence | Scientific review of distributions, sensitivity set and dependence assumptions |
| Unsafe health-loss/cost shortcut | DALY/YLD/YLL/cost case-fraction allocation fails closed with a targeted negative test | resolved locally | Scientific and patient/community interpretation review |
| Correlation and structural scenarios | Bounded named synthetic scenarios are implemented; correlation remains explicitly unsupported with no silent independence claim | partial | Scientific approval of scenario and dependence contracts |
| Track 009 dependency | No ledger activation or downstream interface freeze performed | pending | Track 009 completion |

## Disposition

Keep Track 010 **blocked**. Do not activate burden calculations or freeze interfaces for Track 003 until the evidence and parameter ledger is complete.

### External reviewer packet

- **Scientific/statistical:** approve estimands, compatible units, distributions, dependence, scenarios and uncertainty interpretation.
- **Engineering:** inspect numerical stability, property/golden/convergence tests, reproducibility and API compatibility.
- **Patient/community:** assess interpretation, communication of uncertainty and risk of misuse.
- **Evidence required:** synthetic reference report, benchmark/test results, invalid-operation evidence, review comments and alpha-scope decision.
