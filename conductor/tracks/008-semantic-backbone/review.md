# Track 008 review — Semantic backbone and burden-purpose hierarchy

**Review date:** 2026-07-27  
**Decision:** Blocked pending upstream Track 002 and Track 007 completion

## Findings

- The repository contains semantic schemas, hierarchy/mapping validation, fail-closed mutually-exclusive aggregation, stable fingerprints, and synthetic semantic tests.
- Track 008 has not entered implementation: all substantive implementation tasks remain pending and no v0.4 semantic contract has been frozen.
- Track 002 remains `in_review` pending live-source, licensing, scientific, data-governance and security evidence.
- Track 007 remains `in_review` pending protocol registration, reproducible repository searches, screening/exclusions, independent methods review and patient/community challenge.

## Review boundaries

- Repository validation cannot satisfy upstream scientific, licensing, governance or patient/community gates.
- Starting Track 008 or freezing semantic contracts before those upstream decisions would create uncontrolled scope and ontology drift.

## Disposition

Keep Track 008 **blocked**. Re-run dependency validation when Tracks 002 and 007 are formally complete; only then move Track 008 to active implementation.

### External reviewer packet

- **Semantic/clinical:** approve identifiers, ontology versions, relation meanings, ambiguity and deprecation rules.
- **Patient/community:** assess naming, grouping, stigma and acceptable burden-purpose categories.
- **Engineering:** inspect schema compatibility, cycle/conservation tests, migration and version-diff evidence.
- **Evidence required:** reviewed mapping release, golden fixtures, impact report, comments and explicit freeze decision.
