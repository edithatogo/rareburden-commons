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

## Non-binding RBC-P004 contract boundary

The reference distinguishes aggregate estimands (jurisdiction-period counts,
admissions, mortality, service use and costs) from person-level estimands that
are permitted only inside an approved local node. Every estimand declares
jurisdiction, age range, index date, look-back/look-forward window, denominator,
coding version, cost perspective and missingness state.

Candidate Australian and New Zealand pathways are recorded as questions for the
custodian rather than assumed access: linkage authority, data minimisation,
retention, withdrawal, Indigenous governance, local ethics and disclosure rules
must be resolved before any execution. The synthetic fixture is sufficient only
to test deduplication, multimorbidity retention, repeated admissions, missing
death values and suppression-safe aggregate export.
