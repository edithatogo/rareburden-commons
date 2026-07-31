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
