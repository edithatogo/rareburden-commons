# Track 002 final extraction specification plan

The final extraction specification is a versioned, candidate-bound contract.
It must be generated only from approved estimand rows and exact source packets.

Required fields per extraction:

- source ID, release, URL/endpoint and SHA-256;
- estimand ID and intended claim;
- exact file, sheet, XML path or API parameters;
- geography and year filters;
- field names, units and transformations;
- inclusion/exclusion and missingness rules;
- revision/update and checksum-drift behavior;
- output schema, lineage and retained hash;
- licence/redistribution/cache posture;
- coverage and representativeness limitations;
- scientific and custodian disposition IDs;
- candidate manifest and input digest.

Workflow:

1. Select only rows from `docs/track-002-estimand-matrix.yml` whose status is
   approved or explicitly bounded for preparation.
2. Bind each row to the exact source manifest and candidate digest.
3. Generate machine-readable extraction instructions and a human-readable
   review table.
4. Validate fields, units, geography/year filters and source hashes.
5. Fail closed on missing terms, changed bytes, unsupported fields or an
   unapproved metric/denominator combination.
6. Re-run the panel challenge and obtain the applicable accountable receipts
   before activation.

The initial specification must remain registration-only for WHO and probe-only
for World Bank. No raw third-party bytes are redistributed by this plan.
