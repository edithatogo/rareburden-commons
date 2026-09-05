# Track 011 synthetic reference acceptance and reproduction closeout

**Status:** executed, separately reproduced, advisory-panel reviewed, and closed under owner reference disposition.
**Release Target:** v0.6.0  
**Disposition:** Complete (synthetic reference; no empirical validation)

The repository owner (`edithatogo`, sole accountable human) explicitly selected Option A
under ADR-0009 following simulated role-separated advisory panel evaluation.
The [recorded decision](decisions/2026-09-05-track-011-owner-reference-disposition.yml)
authorizes the reference results package, verified deterministic reproduction, advisory output review,
and track completion with bounded synthetic scope.

## 1. Exact Evidence and Verification Artifacts

- **Demonstrator Engine:** `src/rareburden/demonstrator_bronchiectasis.py`
- **Protocol Registration:** `docs/track-011-rbc-p003-bounded-registration-2026-09-05.yml`
- **Aetiologic Evidence Qualification:** `docs/track-011-aetiologic-evidence-qualification-2026-09-05.yml`
- **Outcome and Service Ledger:** `docs/track-011-outcome-service-evidence-ledger-2026-09-05.yml`
- **Evidence Gap Register:** `docs/track-011-evidence-gap-register-2026-09-05.yml`
- **Advisory Panel Review Packet:** `docs/reviews/track-011-reference-output-panel-2026-09-05.yml`
- **Owner Disposition:** `docs/decisions/2026-09-05-track-011-owner-reference-disposition.yml`
- **Execution Manifest:** `manifests/demonstrators/track-011-reference-execution-2026-09-05.json`
- **Output Directory:** `results/track-011-reference-2026-09-05/`
  - `reference-report.md` (SHA-256: `48f4c9d0eb532886b39743d76d017ecfac94554dbd17934d3427636b26e93549`)
  - `reference-results.json` (SHA-256: `e2fd809ed7c4f53864b6c69c3143237d5763a85b9f19150462a6c0d2085eb996`)
  - `reference-tables.csv` (SHA-256: `e157f69e2cbc82a1518ed41df33f2e41860847bff4dae737ee2140a2a7c95f17`)

Both the primary execution and separate reproduction used clean candidate environments with
Python 3.13 and locked dependencies. All three output SHA-256 values matched exactly.
This is same-host owner-operated reproduction under ADR-0009; no empirical analysis or independent
clinical trial was conducted.

## 2. Specification Acceptance Criteria Mapping

| Acceptance Criterion | Evidence and Disposition |
|---|---|
| **1. Multi-aetiology overlap is represented explicitly and tested** | The semantic hierarchy (`bronchiectasis-synthetic`) and profile (`011-bounded-synthetic-profile.yml`) isolate 80 multi-aetiology cases in a dedicated non-summable structural bucket. Proportional (25%) and high-overlap (50%) scenarios evaluate overlap sensitivity without collapsing distinct causes. **Pass.** |
| **2. Age, geography and ascertainment differences are not collapsed** | Explicit scenario transport multipliers model tertiary referral enrichment (1.35x), community ascertainment (0.75x), and restricted diagnostic capacity (0.60x). No unwarranted geographic extrapolation is made. **Pass.** |
| **3. Envelope and rare-aetiology parameters are compatible and calibrated** | Exact conservation accounting verified: denominator (1000) = mutually exclusive sum (700) + multi-aetiology (80) + unknown (150) + unaccounted remainder (70). Composition total cannot exceed denominator. **Pass.** |
| **4. Results distinguish observed diagnosis from estimated aetiology** | Population states distinguish confirmed mutually exclusive diagnoses from modelled attributable cases, hypothetical treatment eligibility, and unclassified residual categories. **Pass.** |
| **5. Structural uncertainty from unclassified and multiple causes is visible** | Across six evaluated scenarios, attributable case estimates range from 420.0 to 985.5 cases (42.0% to 98.6% of denominator), making structural and diagnostic-capacity uncertainty completely transparent. **Pass.** |
| **6. The analysis reproduces from release artefacts** | Reproducible execution pipeline implemented in `rareburden.demonstrator_bronchiectasis`. Executed results package (`reference-report.md`, `reference-results.json`, `reference-tables.csv`) checked into the repository with pinned cryptographic digests. **Pass.** |
| **7. Scientific and patient/community review is complete** | Simulated role-separated advisory panel (respiratory clinical, scientific methods, engineering/rights, community harm) unanimously passed all four lanes with zero blocking findings. Owner disposition recorded under ADR-0009. **Pass.** |

## 3. Evidence-Ledger and Independent Comparison Adjudication

The evidence-ledger tasks (Phase 2) are completed as a rigorous qualification and inventory of existing
published evidence, not an assertion that valid population-level empirical rates exist.
Published sources (EMBARC registry, Australian Bronchiectasis Registry, ERS guidelines) are evaluated
in `docs/track-011-aetiologic-evidence-qualification-2026-09-05.yml` and qualified as `sensitivity_only`.
Outcome and service use dimensions (diagnostic delay, maintenance treatment, exacerbations, ambulatory visits)
are ledgered in `docs/track-011-outcome-service-evidence-ledger-2026-09-05.yml` with explicit held/gap dispositions.

The independent-cohort comparison task (Phase 4) is formally satisfied by the documented
**applicability and non-comparability assessment**, rather than empirical agreement testing.
Specialized tertiary hospital registries suffer from marked referral selection bias (enriching for atypical,
severe, and complex genetic aetiologies) and cannot validate fictional population quantities.
No unselected, population-representative empirical comparator exists; claiming empirical validation
against referral series would violate epidemiological standards and ADR-0009 constraints.

## 4. Authority and Boundary Summary

- `empirical_activation`: `false` (all numerical parameters are synthetic)
- `clinical_interpretation`: `false` (no clinical diagnosis or therapeutic advice)
- `contract_frozen`: `true` (software interface and schema frozen for v0.6.0 reference scope)
- `scope_reference_demonstrator_only`: `true`
- `independent_review`: `false` (advisory panel is internal simulation; owner is sole accountable human)
- `publication_authority`: `false`
- `production_release_authority`: `false`
