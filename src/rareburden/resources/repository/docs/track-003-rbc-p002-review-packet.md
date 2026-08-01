# Track 003 RBC-P002 review packet

**Status:** non-binding preparation; Track 003 remains blocked  
**Protocol draft:** RBC-P002 v0.1.0  
**Activation rule:** do not freeze entities, denominators or analysis outputs
until Tracks 008, 009 and 010 are complete.

## Decisions required

| Decision | Evidence | Accountable disposition |
|---|---|---|
| Entity/gene/phenotype scope | Versioned semantic release and inclusion/exclusion list | approve, revise or reject |
| Denominator and estimand | Declared geography, period, age band and compatible diabetes envelope | approve, revise or bound |
| Diagnosed/undiagnosed/modelled states | State definitions, ascertainment and penetrance assumptions | approve, revise or reject |
| Evidence and transportability | Ledger records by age, ancestry, setting and referral pathway | approve, revise or bound |
| Outcome/economic interpretation | Subgroup-specific evidence or clearly labelled scenarios | approve, narrow or reject |
| Framing and harms | Patient/community review of language, equity and interpretation | approve, revise or dissent |

## Repository evidence expected

- Synthetic RBC-P002 protocol and analysis specification.
- Semantic IDs and ledger parameter fingerprints for every input.
- Deterministic and seeded simulation outputs with structural/denominator/
  ascertainment/penetrance/referral scenarios.
- Explicit distinction between prevalence, diagnosed prevalence, undiagnosed
  fraction and modelled expected population.
- Reproducible report, limitations, data-access asks and no-compatible-envelope
  failures.

## Safe continuation

Continue synthetic fixtures, schema checks and report scaffolding. Do not freeze
clinical entities, claim cohort representativeness, apply fractions to
incompatible outcomes/costs, or produce empirical estimates before upstream
semantic/ledger/engine contracts and accountable clinical, methods,
data-governance and patient/community review are complete.
