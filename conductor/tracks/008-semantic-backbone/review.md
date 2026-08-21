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

### Bounded source-reconciliation review — 2026-08-16

Repository review result: **Pass for bounded preparation with four unresolved
medium findings**. Eight release records are now deterministically bound to
merged Track 002 evidence. Exact public byte routes are restricted to observed
CC BY 4.0 sources; HPO, UMLS, SNOMED CT and WHO ICD bytes remain private and
their real-world semantic use remains disabled. Negative tests reject activation
claims and unsafe public routing.

The role-separated repository review in
`docs/track-008-bounded-agent-review-2026-08-16.yml` recommends continued
synthetic and metadata-only preparation. Its methods, rights and naming lanes
identify no critical repository-semantic finding, but do not constitute
clinical, scientific, patient/community, custodian or independent approval.
No owner disposition is inferred. Track 008 remains blocked, the parent
source-pinning and panel tasks remain open, and the v0.4 contract is not frozen.

### Freeze-readiness review — 2026-08-21

Repository review result: **Pass for closure-contract preparation only**. The
readiness record enumerates both incomplete upstream dependencies, all four
unresolved medium findings, accountable source and naming evidence, exact
candidate binding, migration impact and freeze-decision requirements. Its
validator rejects hidden findings, premature completion/freeze claims, panel
independence claims and owner-operated work labelled as independent review.
It neither approves ontology pins nor supplies clinical, patient/community or
independent semantic authority; Track 008 therefore remains blocked.

### Bounded completion review — 2026-08-22

Repository review result: **Pass for bounded completion only**. The selective
decision records the exact Orphadata, MONDO and nine HPO ontology-core asset
allowlist, the provisional non-clinical effects, prohibited claims and the
source-rights, clinical-use, community-authority and production-release gates
that remain outside this track's bounded completion. The repository owner is
the sole accountable human; agent-panel output is advisory and is not
independent, clinical, community, custodian or external approval. Track 009
remains blocked on its own evidence and freeze gates.

### Single-owner governance reconciliation — 2026-08-21

Repository governance result: **agent-panel and owner-disposition work is
complete for the bounded provisional non-clinical candidate**. Under ADR-0009,
independent human review is not a repository gate: role-separated agents advise
and the repository owner is the sole accountable decision-maker. The exact
Option A disposition therefore closes the repository review task without
creating an independence claim.

Track 008 remains **blocked and incomplete**. The continuing blockers are
factual or scope-specific: unresolved licence and redistribution terms for
excluded source classes, source-specific mapping fitness, clinical validity,
and actual-community naming authority for any use that would claim community
participation, consent, endorsement or representation. Owner and agent work
cannot self-attest those external facts or authorities.
