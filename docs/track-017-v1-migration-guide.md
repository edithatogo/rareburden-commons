# Track 017 bounded v1 migration guide

**Status:** preparation for a non-production candidate; no stable v1.0.0
migration is declared.

This guide describes the compatibility boundary for a future bounded v1
candidate. It is usable for local rehearsal only until an exact candidate and
release decision are recorded.

## Migration sequence

1. Preserve the source checkout, input manifests, environment lock and output
   hashes for the current candidate.
2. Run the documented checks from `docs/v1-release-candidate-checklist-017.md`.
3. Compare schema and semantic identifiers before loading historical outputs.
4. Regenerate synthetic/reference outputs into a new directory; never overwrite
   a retained evidence package.
5. Record discrepancies, changed assumptions and any rollback decision.

## Compatibility rules

- Existing identifiers, provenance fields and evidence status must not be
  silently reinterpreted.
- Schema or output-contract changes require a versioned migration receipt and
  compatibility tests.
- Unsupported controlled-data, production and empirical workflows must remain
  rejected or explicitly out of scope.
- A migration receipt is evidence of a local transformation, not evidence of
  release authority, publication or external validation.

## Rollback and correction

Keep the prior candidate immutable, mark the new candidate invalid if a hash,
schema or provenance check fails, and issue a dated correction or supersession
notice. Do not rewrite historical receipts.

## Open gates

The exact candidate, owner disposition, release-authority decision, public
publication and post-publication verification are pending. This document does
not close any of those gates.
