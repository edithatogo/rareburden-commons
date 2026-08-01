# Track 008 review — Semantic backbone and burden-purpose hierarchy

**Review date:** 2026-07-27  
**Decision:** Blocked pending upstream Track 002 and Track 007 completion

## Findings

- The repository contains semantic schemas, hierarchy/mapping validation, fail-closed mutually-exclusive aggregation, stable fingerprints, and synthetic semantic tests.
- Track 008 has preparatory implementation (validated schemas, hierarchy/mapping checks, synthetic fixtures and mapping release diffs), but substantive source-pinned semantic release work remains pending and no v0.4 semantic contract has been frozen.
- Track 002 remains `in_review` pending live-source, licensing, scientific, data-governance and security evidence.
- Track 007 remains `in_review` pending protocol registration, reproducible repository searches, screening/exclusions, independent methods review and patient/community challenge.

The repository-owned version-diff gap is now addressed by `diff_mapping_sets`,
which emits deterministic added, removed and changed source-code lists plus
release fingerprints. Focused semantic tests pass. This does not activate a
semantic contract or substitute for source-release and clinical review.

### Review rerun — 2026-07-29

Repository review result: **Pass with dependency blockers**. The semantic
implementation evidence and version-diff tooling are internally consistent, and
the full project validation gate passes. Track 008 remains blocked pending Track
002 source/licence evidence, Track 007 external review, and clinical and
patient/community approval of identifiers, naming and aggregation semantics.

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

### External-gate panel synthesis — 2026-08-01

The preparatory panel report (`docs/v1-subagent-panel-report-017.md`) supports
continued synthetic implementation only. It does not close the upstream
source/licence or landscape challenge gates, nor does it approve identifiers,
naming or aggregation semantics. Track 008 therefore remains blocked and its
contract remains non-binding.

### Preparation refresh — 2026-08-01

`docs/track-008-semantic-review-packet.md` records the exact semantic, clinical,
patient/community and engineering decisions required before activation. It is
repository-owned preparation and does not freeze the v0.4 contract.
