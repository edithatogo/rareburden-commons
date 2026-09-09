# Track 008 specification — Semantic backbone and burden-purpose hierarchy

## Objective

Implement a versioned semantic layer that defines rare-disease entities, maps relevant coding systems and supports mutually interpretable burden aggregation without silent double counting.

## Required outputs

- disease-definition and ontology-mapping schemas;
- pinned ORDO/ORPHA, ICD-10/11, MONDO, OMIM, HPO and selected terminology releases;
- mapping provenance, confidence and ambiguity representation;
- burden-purpose hierarchy or linearisation for supported demonstrators;
- parent/child, syndrome/aetiology and multi-diagnosis overlap rules;
- version-diff and migration tooling;
- human-readable mapping reports and machine-readable releases;
- golden fixtures for difficult and ambiguous cases.

## Acceptance criteria

1. Every supported disease entity has a stable internal identifier and source-version references.
2. One-to-many and uncertain mappings remain explicit rather than being forced.
3. Mutually exclusive aggregation nodes pass conservation and no-parent-child-sum tests.
4. Demonstrator definitions can be reconstructed from the semantic release alone.
5. Ontology updates produce a reviewable diff and invalidate affected outputs.
6. An owner-operated, role-separated simulated community-impact challenge
   addresses naming and aggregation harms without claiming participation,
   representation, consent, endorsement or authority for unrelated communities.
7. Semantic releases have migration and deprecation rules.

## Non-goals

- replacing source ontologies;
- declaring clinically authoritative variant classifications;
- forcing every rare disease into a mutually exclusive global tree;
- hiding unresolved semantic uncertainty.

## v1 contribution

This track implements the disease-definition, mapping and overlap controls required by V1-SCI-02 and V1-DATA-05.

## Non-binding protocol draft — semantic contract v0.1.0 (2026-07-27)

Preparatory only; this does not activate the track or freeze a v0.4 interface. Represent disease, syndrome, aetiology, phenotype and code-system entities with stable internal IDs, source/version, relation, validity, provenance and licence state. Support exact, broader, narrower, approximate, ambiguous, deprecated and unmapped mappings, with ambiguous aggregation failing closed. Explicitly represent mutually exclusive nodes, non-tree relations, multi-aetiology and multi-diagnosis links. Validate cycles, conservation, version impact and golden fixtures; require role-separated semantic, clinical-methods, simulated community-impact and engineering agent advice followed by repository-owner disposition. Independent human review is not part of this single-person repository model. Factual source-rights constraints, clinical-validity limits and authority for unrelated communities remain separate and cannot be manufactured by owner or agent attestation.
