# Track 003 RBC-P002 review packet

**Status:** bounded interface registration active; data execution disabled

**Protocol:** RBC-P002 v0.2.0-bounded

**Activation rule:** Tracks 008, 009 and 010 are complete within bounded scope.
Do not freeze clinical genes/phenotypes or execute synthetic, public-aggregate
or controlled-data analyses until a compatible exact parameter set is qualified.

## Decisions required

| Decision | Evidence | Accountable disposition |
|---|---|---|
| Entity/gene/phenotype scope | Versioned semantic release and inclusion/exclusion list | approve, revise or reject |
| Denominator and estimand | Declared geography, period, age band and compatible diabetes envelope | approve, revise or bound |
| Diagnosed/undiagnosed/modelled states | State definitions, ascertainment and penetrance assumptions | approve, revise or reject |
| Evidence and transportability | Ledger records by age, ancestry, setting and referral pathway | approve, revise or bound |
| Outcome/economic interpretation | Subgroup-specific evidence or clearly labelled scenarios | approve, narrow or reject |
| Framing and harms | Simulated-community/harm agent challenge of language, equity and interpretation | advise revise, bound or stop; never community approval |

## Repository evidence expected

- Synthetic RBC-P002 protocol and analysis specification.
- Semantic IDs and ledger parameter fingerprints for every input.
- Deterministic and seeded simulation outputs with structural/denominator/
  ascertainment/penetrance/referral scenarios.
- Explicit distinction between prevalence, diagnosed prevalence, undiagnosed
  fraction and modelled expected population.
- Machine-tested framing and interpretation guard covering evidence labels,
  uncertainty, denominator visibility, harm/equity challenges, acceptable use
  and stop triggers.
- Machine-tested aetiologic-fraction evidence contract covering source
  registration, aligned extraction, quality domains, stratification,
  conflicts/overlap, missingness and accountable verification states.
- Machine-tested, empty outcome and service-use evidence-ledger contract that
  separates diagnosis-delay time origins, treatment change from benefit,
  complication measure types, people from encounters, causal from descriptive
  claims, and sampling from structural and transportability uncertainty.
- Reproducible report, limitations, data-access asks and no-compatible-envelope
  failures.

## Safe continuation

Continue bounded contract checks, agent challenge and exact public-aggregate
qualification. Do not freeze clinical entities, claim cohort representativeness,
apply fractions to incompatible outcomes/costs, or produce an estimate before
a protocol-compatible parameter set and its rights/provenance receipts pass.

The non-binding framing guard is
`docs/track-003-framing-interpretation-guard-v0.1.0.yml`. It prepares review
questions and fail-closed language only; it is not patient/community consent,
clinical approval or an owner disposition.

The non-binding evidence contract is
`docs/track-003-aetiologic-fraction-evidence-contract-v0.1.0.yml`. It contains
no registered source release or extracted value and does not establish a
systematic search, verified evidence, an empirical parameter or fitness for use.

The non-binding outcome and service-use ledger contract is
`docs/track-003-outcome-service-evidence-ledger-contract-v0.1.0.yml`. It is
empty and does not establish empirical diagnosis delay, treatment effects,
complication or service-use differences, causal validity or transportability.
