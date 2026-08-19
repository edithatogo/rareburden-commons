# Track 010 dependency review — Public burden engine and uncertainty framework

**Review date:** 2026-07-27  
**Decision:** Bounded synthetic preparation; empirical activation remains blocked

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

Property tests cover bounded population products; a versioned golden simulation
vector protects the deterministic random contract; a seeded beta reference
checks convergence toward its analytic mean; and overflow or negative simulated
products now fail closed rather than entering summaries.

### Blocker resolution matrix — 2026-07-29

| Blocker | Repository action | Status | Remaining gate |
|---|---|---|---|
| Undefined alpha estimands | Synthetic reference defines affected-population and rare-aetiology cases, units and invalid operations | resolved locally | Scientific/statistical approval |
| Unbounded uncertainty behaviour | Seeded propagation records seed/draws/unit; independent-product decomposition and structural sensitivities have deterministic coverage | resolved locally for independence | Scientific review of distributions, sensitivity set and dependence assumptions |
| Unsafe health-loss/cost shortcut | DALY/YLD/YLL/cost case-fraction allocation fails closed with a targeted negative test | resolved locally | Scientific and patient/community interpretation review |
| Correlation and structural scenarios | Bounded named synthetic scenarios are implemented; correlation remains explicitly unsupported with no silent independence claim | partial | Scientific approval of scenario and dependence contracts |
| Track 009 dependency | No ledger activation or downstream interface freeze performed | pending | Track 009 completion |

## Disposition

Keep Track 010 **blocked for empirical or production use**. Track 009's
repository-owned source-release binding is now complete enough to execute the
exact synthetic assurance receipt, but it activates no empirical source and
freezes no interface for Track 003.

### Track 009 reconciliation — 2026-08-16

The engine now validates the exact Track 009 source-release binding manifest
before execution. The committed deterministic receipt is synthetic-only,
retains the binding digest and quality-disposition identifier, and explicitly
records `contract_frozen: false` and `empirical_parameter_activation: false`.
Negative tests reject primary-estimate use, activation or premature freeze.

This resolves the stale Track 009 dependency for repository-owned synthetic
assurance only. Scientific-software agent-panel review, owner disposition and
any exact empirical source/estimand activation remain open.

### External reviewer packet

- **Scientific/statistical:** approve estimands, compatible units, distributions, dependence, scenarios and uncertainty interpretation.
- **Engineering:** inspect numerical stability, property/golden/convergence tests, reproducibility and API compatibility.
- **Patient/community:** assess interpretation, communication of uncertainty and risk of misuse.
- **Evidence required:** synthetic reference report, benchmark/test results, invalid-operation evidence, review comments and alpha-scope decision.

### External-gate panel synthesis — 2026-08-01

The preparatory panel report (`docs/v1-subagent-panel-report-017.md`) does not
replace scientific/statistical, patient/community or engineering review. The
bounded synthetic engine may continue to be tested, but Track 010 remains
blocked by Track 009 and no alpha interface or dependence contract is frozen.

### Preparation refresh — 2026-08-01

`docs/track-010-engine-review-packet.md` records the exact estimand,
uncertainty, dependence, structural-scenario, prohibited-shortcut and alpha
freeze decisions required before activation. It is repository-owned preparation
and does not replace scientific, engineering or patient/community review.
