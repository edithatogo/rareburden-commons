# Track 014 dependency review — Atlas, API and reproducible release engineering

**Review date:** 2026-07-29  
**Decision:** Planned; implementation entry blocked by upstream release evidence

## Findings

- Tracks 002, 009, 010 and 013 are not complete, so no reviewed aggregate release
  exists for an atlas or API build.
- Local release-manifest, provenance, lineage and reproducibility primitives are
  available, but no public product or mutable dashboard has been activated.
- Scientific, patient/community, data-governance, security, accessibility and
  release gates remain required.

## Local preparation

`docs/atlas-release-014-reference.md` records the immutable reviewed-artifact
boundary, missingness rule, aggregate-only publication boundary and shared
release-fingerprint requirement. It is preparatory documentation, not a beta
release or publication authorization.

## Required gates before activation

- Track 013 approval of quality, equity and gap-map outputs.
- Reviewed source/parameter manifests and a release-content audit.
- Accessible static/API consistency tests and independent reproduction.
- Release authority approval for archive/DOI and public publication.

## Preparation refresh — 2026-08-01

`docs/track-014-atlas-api-review-packet.md` now records the exact evidence and
accountable decisions required for the reviewed-artifact boundary, public
output rights, semantic/accessibility controls, consistency, independent
reproduction and release. This is non-binding preparation; no atlas, API,
beta, archive or DOI has been activated.

## Repository-owned release-surface review — 2026-08-15

The static-first bounded slice now produces a schema-valid prepared release
surface only when the aggregate package and read-only API projection agree and
every input artifact carries an exact digest, repository review receipt and
explicit redistributable or metadata-only disposition. Negative tests reject
projection drift, unresolved rights, missing receipts and invalid digests.

This closes the repository-owned construction task only. Accessibility,
independent reproduction, upstream scientific/governance dependencies, release
authority, archive/DOI creation and public beta activation remain pending.

## Repository-owned lifecycle-metadata review — 2026-08-15

The prepared surface now has a deterministic correction, withdrawal and
supersession representation. Each notice binds the exact affected surface,
preserves the original candidate, requires an exact different replacement for
correction or supersession, forbids an implied replacement on withdrawal, and
is revalidated before projection. Static and API consumers can use the same
schema-valid status object and text alternative. Tampering, cross-candidate
notices, duplicate identifiers and ambiguous lifecycle transitions fail closed.

This is repository lifecycle evidence only. It does not show that a public
release was corrected or withdrawn, and it does not satisfy accessibility,
independent reproduction, upstream authority or release-authority gates.

## Bounded Track 008–013 reconciliation — 2026-08-16

Repository review result: **Pass for a local synthetic/static projection**.
The static model, aggregate package, read-only API shape and lifecycle status
share exact identifiers, preserve missingness and `not_assessed` sufficiency,
and remain publication-unauthorized. A withdrawal propagates `do_not_use` and
an accessible text alternative without mutating the candidate. Negative tests
reject dependency drift, surface mismatch, sufficiency upgrades and release
overclaims.

Track 014 remains **planned and non-public**. Accessibility, real-source
activation, separately executed reproduction, release authority and explicit
public/stable release decisions remain pending.
### Implementation checkpoint — 2026-08-01

The repository-owned release boundary was implemented and rechecked. Release
manifests are schema-constrained and content-addressed; verification rejects
manifest identity, repository-state and artefact-integrity mismatches. The
offline reference workflow and research-object checks preserve provenance and
do not activate an atlas, API, mutable dashboard, or public data publication.

Track 014 remains **Planned** rather than Active because its dependencies are
not complete. The atlas/API contracts, accessibility review, reviewed-artifact
inputs, independent reproduction, archive/DOI authority, and Track 013
approval remain release gates. No external approval or beta publication is
inferred from the local checks.

### Review rerun — 2026-08-01

The implementation checkpoint was reviewed against every acceptance criterion.
The local manifest, provenance, hash, research-object and clean-reference
checks are passing and the aggregate-only boundary is explicit. No defect was
found in the repository-owned slice.

The remaining findings are release-blocking scope, not fixable local defects:
the prerequisite tracks are incomplete; no reviewed aggregate release exists;
user journeys, API/package contracts, accessibility review, static/package/API
consistency, independent reproduction, archive/DOI authority and release
content audit are outstanding. Track 014 remains **Planned** and is not
archive-eligible. No atlas/API beta or public publication is authorised by
this review.

## Plan-state reconciliation — 2026-08-21

Later bounded evidence supersedes the stale API/package-contract and parity
findings above. The static page, aggregate package, read-only API,
release-surface schemas, reviewed-artifact boundary,
citation/provenance/licence/digest fields, parity tests, text alternatives and
disabled-publication invariant are implemented for synthetic preparation.

This does not complete user research, uncertainty and quality presentation, a
full demonstrator/country product, independent accessibility review,
archive/DOI workflow, clean independent reproduction, real-source activation
or any beta/public release decision. Track 014 therefore remains Planned; this
reconciliation corrects task states without claiming publication, external
review or release authority.

## Bounded user journeys — 2026-08-21

Five repository-authored journeys now define the intended decision path for
patient/family organisations, policy/public-health users, researchers,
custodian operators and funder/payer/HTA users. Each lane identifies its entry
point, decisions, outputs, required evidence and fail-closed stop conditions.

The journeys are explicitly design hypotheses. They do not constitute user
research, patient/community endorsement, accessibility acceptance, custodian
approval, funding endorsement or release authority. Real-user and independent
accessibility evidence remain pending before a public candidate can rely on
these journeys as validated usability evidence.

## Evidence-presentation component contract — 2026-08-21

Repository review result: **Pass for the bounded design contract and synthetic
fail-closed scenarios**. One schema-validated contract defines provenance,
uncertainty, domain-level quality and explicit missingness components, then
maps the same scientific facts into the five repository-authored journey
profiles. Positive scenarios preserve explicit uncertainty and null
missingness; negative scenarios reject missing-as-zero, unexplained uncertainty
and opaque composite quality scores.

This closes only the repository-owned component-definition task. It does not
show that any interface is understandable or accessible to real users, that a
source is cleared for redistribution, that an exact candidate was reproduced,
or that publication is authorised. Independent accessibility and real-user
usability evidence remain pending.

## Accessibility preparation and bounded static product set — 2026-08-21

Repository review result: **Pass for contract-level accessibility preparation
and three synthetic static product models**. The shared release identity now
projects into gap, synthetic-country and demonstrator products with required
headings, text alternatives, explicit non-colour status labels, visible
`not_assessed` state and missing-not-zero semantics. Synthetic country
identifiers are restricted to the ISO user-assigned `XAA`–`XZZ` range so they
cannot silently represent a real jurisdiction.

The repository-owned accessibility review remains advisory and records
keyboard/assistive-technology behavior and plain-language comprehension as not
independently assessed. The main accessibility design-review task therefore
remains pending, as do real-user evidence, patient/community acceptable-use
review and public-candidate authorization. The product-set task is complete
only for the bounded synthetic/static implementation; it does not establish an
empirical country profile, public demonstrator or released gap atlas.
## Review rerun — 2026-08-22

**Finding (High, remediated):** the bounded-runtime optimization in
`rareburden.assurance._logical` checked containment lexically but did not
reject symlinked descendant directories. A pre-existing symlink below an
operator-chosen output path could have caused an artefact to be written outside
the declared root while retaining an in-root logical identifier.

**Fix:** commit `45dad19` preserves the lexical runtime improvement and rejects
every symlinked descendant before an artefact receives a logical path. A focused
test exercises the escape attempt; the reference workflow remains reproducible.

**Disposition:** repository review passes after remediation. Track 014 remains
Planned: independent accessibility and real-user usability evidence, archive or
DOI workflow, separately executed reproduction, real-source rights and release
authority are all still required.

## Blocker disposition — 2026-08-22

Track 014 is **Blocked**, not Complete or Archived. The repository-owned
synthetic/static implementation and review remediation pass all local gates,
but the acceptance-critical boundaries remain unresolved:

- independent accessibility review and real-user usability evidence;
- clean-environment and separately executed reproduction;
- archive/DOI authority and immutable research-object release;
- Track 013 approval and real-source redistribution rights;
- exact owner release-content and beta/public-release decision.

These are represented as machine-readable pending gates in `metadata.json`.
No archive move is authorized: archiving an incomplete, non-superseded track
would destroy lifecycle meaning and overstate release readiness. Reopen the
track only when the named evidence is supplied or the scope is formally
superseded with an accountable decision.
