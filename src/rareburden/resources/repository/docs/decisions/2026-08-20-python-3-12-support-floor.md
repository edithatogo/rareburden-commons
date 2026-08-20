# Python 3.12 support floor

**Decision date:** 20 August 2026

**Status:** Accepted by the repository owner

**Scope:** Reference package, CI compatibility matrix and declared wheelhouse contract

## Decision

The supported Python range is 3.12 through 3.14. Python 3.11 and Python 3.15 or
later are outside the current support contract. Python 3.13 remains the
normative release-build and cross-platform portability runtime; this decision
does not expand platform, controlled-node or production-readiness claims.

The package metadata, Linux CI matrix, static-analysis targets, wheelhouse
schema and current user/governance documentation must express the same range.
The locked dependency resolution must be regenerated against the new lower
bound. Historical records of earlier Python 3.11 testing remain historical and
do not establish current support.

## Trade-off and contingency

Removing Python 3.11 reduces the compatibility and maintenance surface and
aligns the implementation with the existing Python 3.12-or-later code style.
It may exclude secure or institutional environments that have not upgraded.
Those environments require an explicitly maintained local variant or a later,
separately recorded support decision; successful ad hoc execution is not enough
to restore support.

## Minimum evidence

- package and lock metadata reject Python versions below 3.12;
- hosted Linux checks pass on Python 3.12, 3.13 and 3.14;
- the Python 3.13 release and cross-platform assurance jobs remain green; and
- repository checks verify synchronized runtime assets and schema contracts.

This is repository-owner engineering approval only. It is not external review,
release approval, controlled-node accreditation or evidence of compatibility
outside the declared matrix.
