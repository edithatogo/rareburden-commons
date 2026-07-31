# Track 003 specification — Monogenic diabetes rare-within-common demonstrator

## Objective

Produce the first end-to-end reference analysis showing how rare monogenic aetiologies can be estimated within a common diabetes burden envelope without requiring the same people to occur in every source.

## Scientific question

For a defined geography, period, age and diabetes denominator, what proportion and number of people plausibly have a specified monogenic diabetes aetiology, with what diagnostic, treatment, outcome and economic implications?

## Required outputs

- demonstrator protocol RBC-P002;
- versioned inclusion list and phenotype/genotype definitions;
- explicit denominator and competing denominator sensitivity analyses;
- evidence ledger for aetiologic fractions, diagnosis delay, treatment change and outcomes;
- public/synthetic reference dataset and analysis specification;
- deterministic and simulation-based estimates with uncertainty;
- sensitivity to age, ancestry, ascertainment, penetrance and referral bias;
- health and economic interpretation that does not apply a case fraction blindly to incompatible envelopes;
- reproducible report, tables, code and review response.

## Acceptance criteria

1. Disease entities and denominator populations are unambiguous and versioned.
2. Every parameter has provenance, evidence status, quality and transportability metadata.
3. Primary and sensitivity estimates reproduce from the release package.
4. The analysis distinguishes prevalence, diagnosed prevalence, undiagnosed fraction and modelled expected population.
5. Outcome and cost estimates use subgroup-specific evidence or are labelled as scenarios.
6. Uncertainty and structural assumptions are visible in all headline results.
7. Independent diabetes/genetics and methods reviewers approve or have their dissent documented.
8. Patient/community review confirms acceptable framing and interpretation.

## Non-goals

- clinical diagnosis or individual variant interpretation;
- a claim that one cohort is nationally representative without validation;
- a causal treatment-effect estimate from ecological evidence;
- a definitive global monogenic-diabetes total in the first demonstrator.

## v1 contribution

This is the reference rare-within-common analysis for V1-SCI-05 and validates the semantic, ledger and burden-engine contracts.

## Non-binding protocol draft — RBC-P002 v0.1.0 (2026-07-27)

Preparatory only; this does not activate the track or freeze dependent contracts. For a declared geography, period, age band and diabetes denominator, estimate monogenic case count and proportion, separating diagnosed, undiagnosed and modelled states. Inputs are versioned semantic entities and ledger parameters for aetiologic fraction, ascertainment, penetrance, referral, outcomes and costs. The primary model is a compatible envelope-times-fraction calculation with seeded simulation; sensitivities cover denominator, age, ancestry, setting, ascertainment, penetrance and referral. Outputs include uncertainty, parameter fingerprints, limitations and reproducibility metadata. Clinical/genetics, epidemiology, patient/community, governance and engineering review are required.
