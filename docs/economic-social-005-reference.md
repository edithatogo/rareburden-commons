# Track 005 economic and social burden reference contract

**Status:** non-binding repository draft; not a registered protocol, co-design
record, valuation study, or approved economic analysis.

## Perspectives and component taxonomy

Report components separately before any aggregate total:

1. health-system/payer: direct medical and health-service resource use;
2. household: out-of-pocket costs, unpaid care time and household adaptation;
3. societal: the declared combination of payer, household, education and
   productivity components, with transfers identified rather than double-counted.

Each component records payer/recipient, quantity, unit, source, evidence status,
population, period, currency, price year and transformation. Caregiver time,
education disruption, productivity and social participation are not collapsed
into a single quality score.

## Currency, price year and transfer rules

Every monetary value must declare an ISO currency and price year. Conversion is
an explicit transformation with source, date and method; no implicit exchange
rate or PPP conversion is permitted. PPP is used only when the estimand calls for
real-resource comparison and records the PPP source and base year. Discounting
records rate, perspective, time horizon and whether costs or outcomes are
discounted. Transfer payments are excluded from societal resource totals and
reported separately; they may remain in a payer or household cash-flow view.

## Overlap, missingness and subgroup reporting

The same event cannot be counted as both a payer cost and a societal resource
without an explicit transfer relationship. Missing components are reported as
`not_collected`, `not_permitted`, `not_comparable`, or `not_estimable`; they are
never silently zero-filled. Results expose distributional subgroups and who is
missing from the evidence, using locally meaningful categories and approved
governance rather than imported classifications.

## Survey and acceptable-use safeguards

Patient/family survey instruments require co-design, translation/adaptation,
accessibility review, remuneration for participant expertise, a burden budget,
withdrawal and consent language, and a documented data-governance decision.
Until those gates are complete, the repository permits synthetic fixtures and
metadata-only plans but no participant data collection or public individual-level
outputs.

This contract is preparatory evidence only. It does not set a monetary value on
unpaid care, establish equity weights, or authorize linkage, collection, or
publication of patient/family data.
