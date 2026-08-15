# Track 012 synthetic linked-data reference

`examples/paediatric/linked-data-synthetic.yml` is a fully invented fixture for
offline contract work. It contains person, diagnosis, admission, death and cost
tables, including repeated diagnoses (multimorbidity), repeated admissions and a
missing death value.

The fixture’s rules preserve multiple diagnoses, keep admissions distinct, and
require disclosure thresholds before any aggregate export. It is not a schema
for a real custodian dataset and does not authorise linkage or person-level
access. Australian/New Zealand pathways, Indigenous governance, observation
windows, coding packages, suppression thresholds and economic estimands require
custodian and community review before activation.

## Bounded dependency reconciliation

The 2026-08-16 receipt at
`manifests/demonstrators/track-012-bounded-synthetic-receipt-2026-08-16.json`
binds exact repository-owned artifacts from Tracks 004, 005 and 008–011. It
reports deduplicated synthetic people, multimorbidity, utilisation, missing
mortality and cost coverage, and threshold-suppressed jurisdiction rows without
emitting person identifiers or imputing missing values.

This exercise remains synthetic and non-clinical. It does not establish a
paediatric disease definition, administrative-data coverage, economic or
policy interpretation, country transportability, controlled-data access or a
frozen RBC-P004 contract.
