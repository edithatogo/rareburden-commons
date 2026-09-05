# RBC-P001D economic and social burden protocol

**Version:** 0.1.0 (non-binding preparation)  
**Status:** synthetic and metadata-only; not frozen, activated, or approved

This protocol defines the contract shape for economic and social burden work.
It is a repository-owned methods artifact. It does not constitute health-
economics, ethics, patient/community, custodian, or owner approval.

## Perspectives

Report each perspective separately before any comparison or aggregate:

- **Health-system:** direct medical and social-care resources paid by or
  attributable to the health system.
- **Household:** out-of-pocket spending and unpaid household or caregiver time.
- **Societal:** the declared combination of health-system, household,
  productivity, education, and participation components after overlap review.

Every component must declare its perspective, payer, bearer, recipient,
beneficiary, time provider, population, geography, observation period, unit and
denominator. A perspective label is not evidence that a role or transfer was
observed.

## Valuation contract

Monetary-shaped inputs must carry, without defaults:

1. currency and price year;
2. exchange-rate or PPP method, base and source release;
3. discount rate, time horizon and discounting convention;
4. transfer-payment treatment for the declared perspective; and
5. source, transformation and uncertainty references.

Until these fields are reviewed and frozen, monetary-shaped values remain
unvalued. Currency, price year, PPP and discounting must never be mixed or
silently converted. Transfers are costs to one perspective and receipts to
another, not automatically additional societal resources.

## Components and missingness

Keep direct medical, direct non-medical, social-care, out-of-pocket,
caregiver-time, productivity, education and participation components separate.
Use the following measurement states:

| State | Meaning | Permitted interpretation |
| --- | --- | --- |
| `explicit_value` | a quantity was observed or declared for the fixture | report with provenance/status |
| `explicit_zero` | zero was explicitly observed | report as zero, not missing |
| `missing` | expected value is absent | report missing; do not impute silently |
| `not_collected` | the collection did not seek the field | report a data gap |
| `unassessed` | coverage or quality has not been established | do not aggregate |
| `not_applicable` | the field does not apply | do not treat as zero |

Possible or unassessed overlap blocks aggregation. Aggregation is allowed only
for components with the same perspective, unit, denominator basis and declared
observation context, with an assessed no-overlap relationship. Components are
reported separately even when an aggregate is technically eligible.

## Survey and burden safeguards

The patient/family core must be adapted and translated with affected
communities before collection. Adaptation, translation, accessibility,
remuneration, consent, data minimisation, withdrawal and support arrangements
must be recorded. No survey or interview is to be commissioned from this
repository preparation alone, and unpaid community labour must not be assumed.

## Equity and interpretation

Report who bears each component, who may benefit, who is absent, and which
missing data could change the decision. Show subgroup denominators and
suppression rules. Distinguish observed, imputed, transferred and scenario-based
quantities. Synthetic calculations are reference outputs only and must be
labelled non-empirical.

## Activation boundary

RBC-P001D remains non-binding until the owner records a disposition after the
required health-economics, ethics, governance and patient/community review.
No universal monetary burden, patient/family collection, empirical estimate,
production integration, publication, or release is authorized by this draft.
