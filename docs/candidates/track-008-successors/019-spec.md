# Candidate specification — 019 bounded semantic infrastructure

## Objective

Maintain versioned, non-clinical semantic infrastructure with stable internal
identifiers, explicit mapping uncertainty, hierarchy and overlap controls, and
deterministic migration tooling.

## Required outputs

- disease-definition and ontology-mapping schemas;
- an exact allowlist for unmodified source assets and separate synthetic fixtures;
- mapping provenance, confidence and ambiguity representation;
- bounded hierarchy, linearisation and overlap controls;
- version-diff, invalidation, migration and deprecation tooling;
- synthetic/internal reports, releases and difficult-case fixtures.

Source-derived mapping and extracted-label artifacts already exposed in Git are
not authorized for additional repository-owned publication, export, rendering,
activation or promotion by this track. Historical Git availability persists.

## Acceptance criteria

1. Stable identifiers and exact source-version references are enforced.
2. Uncertain, one-to-many and unsupported mappings fail closed.
3. Conservation, parent-child and overlap tests pass on the exact candidate.
4. Synthetic demonstrators reconstruct from the bounded release.
5. Updates produce reviewable diffs and invalidate affected outputs.
6. Migration and deprecation rules are machine tested.
7. Unknown semantic-use modes deny by default.
8. Every distributed exact-unmodified asset has exact source-specific rights,
   route, hash, attribution and notice evidence.
9. The two already-public derived artifacts remain unavailable for additional
   repository-owned publication, export, rendering, activation or promotion
   unless Track 020 and exact derivative-rights evidence both pass.

## Non-goals

- clinical or diagnostic fitness;
- patient/community naming authority or acceptability;
- derivative rights clearance;
- comprehensive, multilingual, geographic or representative coverage;
- public-facing, empirical or authority-bearing semantic activation.

## v1 contribution

Provides only the bounded repository controls within V1-SCI-02 and V1-DATA-05.
It cannot satisfy their empirical, clinical, rights or community-assurance parts.
