# Track 005 specification — Patient, family, economic and social burden module

## Objective

Create transparent, perspective-specific methods and data contracts for health-system, household, caregiver, education, productivity and wider social burden.

## Required outputs

- protocol RBC-P001D for economic and social burden;
- component taxonomy and machine-readable cost/outcome parameter schema;
- declared perspectives, price year, currency/PPP, discounting and transfer-payment rules;
- direct health, social-care, out-of-pocket, caregiver-time, productivity and education modules;
- patient/family survey core with adaptation and translation guidance;
- distributional and subgroup reporting plan;
- missingness and double-counting controls across cost components;
- synthetic examples and reference calculations;
- uncertainty and scenario analysis;
- patient/community, health-economics and ethics review.

## Acceptance criteria

1. Components are reported separately before any aggregate societal total.
2. Analyses cannot mix perspectives, currencies or price years silently.
3. Caregiver time and productivity assumptions are explicit and sensitivity-tested.
4. Transfer payments are handled according to the declared perspective.
5. Survey items are co-designed and do not impose uncompensated data labour on communities.
6. Distributional results expose who bears costs and benefits.
7. Synthetic examples reproduce and pass unit/contract tests.
8. Published economic results state whether they are observed, imputed, transferred or scenario-based.

## Non-goals

- a single universal monetary value for rare disease;
- combining incompatible willingness-to-pay, accounting and welfare measures;
- treating unpaid care as valueless because market prices are absent;
- collecting patient/family data before governance and resourcing are approved.

## v1 contribution

This track supports V1-SCI-05, V1-GOV-04 and the economic parts of the atlas and demonstrators.

## Non-binding protocol draft — RBC-P001D v0.1.0 (2026-07-27)

Preparatory only; this does not activate the track or freeze ledger/engine contracts. Report health-system, household and societal perspectives separately across direct medical, direct non-medical, informal care/time, productivity, education and social participation components. Each parameter carries payer/recipient, currency, price year, PPP, discounting, transfer-payment and evidence metadata. Analyses report per-person and aggregate burden, missingness, equity subgroups and valuation/discounting scenarios without applying case fractions directly to incompatible outcomes. Health-economics, ethics, patient/family, governance and engineering review are required.
