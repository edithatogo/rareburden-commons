# Track 014 implementation plan — atlas/API and release surface

**Status:** repository-owned planning; no atlas/API publication or beta release
is activated by this plan.

## Dependency order

1. **Reviewed-release contract:** finalize the release-manifest profile, input
   allowlist, licence/evidence/uncertainty/limitations requirements, aggregate-
   only rule, release fingerprint and correction/withdrawal metadata.
2. **Static product core:** generate an accessible static demonstrator and gap
   product from one immutable synthetic/reviewed release; preserve missingness
   and display evidence status, uncertainty and limitations.
3. **Package projection:** emit the same release as a versioned aggregate data
   package with schema, citation, checksums and provenance.
4. **API projection:** expose read-only versioned endpoints over the package;
   responses must carry the release fingerprint and never query mutable working
   tables or participant data.
5. **Consistency and accessibility:** compare static, package and API records,
   test text alternatives and non-colour-only semantics, then run clean-build
   validation.
6. **External gates:** obtain Track 013 approval, accessibility/community,
   data-governance, security, independent-operator and release-authority
   dispositions before any v0.8 beta or DOI publication.

## Options

### Option A — Static-first, package-backed (recommended)

Build the static demonstrator and gap products first, then generate the
aggregate package and a narrow read-only API from the same manifest. This
minimizes mutable-service risk, reuses the existing gap-map and release
verifier, and produces useful review evidence before API complexity is added.

**Contingency:** if upstream reviewed inputs are unavailable, use only the
existing synthetic release and label every output synthetic/metadata-only; if
package/API parity cannot be proven, ship the static product as a draft and
keep package/API publication disabled.

### Option B — Package/API-first

Define the data package and versioned API contract before building pages. This
optimizes downstream machine use but increases the risk of freezing schemas
before Track 009/010/013 decisions and requires earlier compatibility work.

**Contingency:** restrict the API to a read-only fixture endpoint and postpone
compatibility guarantees until a reviewed release exists.

### Option C — Full atlas/API stack in one pass

Implement information architecture, static products, package, API,
accessibility and archive workflow together. This offers the broadest demo but
has the highest coupling and the largest rollback surface.

**Contingency:** split at the manifest boundary; retain only schema/tests and
disable all publication routes until every gate passes.

## Recommendation and rationale

Proceed with **Option A**. It satisfies the specification's immutable-release
and aggregate-only constraints earliest, uses existing release/gap-map
building blocks, keeps unsupported estimates out of the product, and leaves a
clean escape hatch if upstream evidence or external gates remain blocked.

## Exit evidence

- release manifest and input allowlist with content fingerprints;
- static/package/API parity report;
- missingness, uncertainty, evidence-status and limitation fixtures;
- accessibility/text-alternative and correction/withdrawal tests;
- clean-build transcript and independent-operator receipt;
- accountable Track 013, data-governance, security and release dispositions.

