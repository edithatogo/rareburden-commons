# Track 014 release-surface reference

Track 014 must build public products only from immutable, reviewed aggregate
artefacts. The existing release-manifest, provenance, lineage, citation and
reproducibility schemas provide the local building blocks, but no atlas/API
product is activated by this document.

The release boundary is:

1. accept only artefacts with a verified manifest, licence state, evidence status,
   uncertainty and limitations;
2. preserve missingness as missing, never as zero;
3. expose correction, withdrawal and supersession metadata alongside versions;
4. publish only aggregate, disclosure-safe outputs;
5. require static, package and API representations to share the same release
   fingerprint before publication.

## Correction, withdrawal and supersession status

`build_atlas_release_notice` creates an immutable notice bound to the exact
prepared release-surface fingerprint. Correction and supersession notices must
name a different exact replacement; withdrawal notices cannot imply a
replacement. `build_atlas_release_status` revalidates every notice before it
creates the shared machine-readable status and accessible text alternative.
The status always keeps `publication_authorized: false`; it is suitable for
static and API-shaped consumers but does not publish or authorize a release.

Track 013 approval, independent reproduction, accessibility review and release
authority remain mandatory before any v0.8 beta publication.

## Static/package/API consistency rehearsal

The repository-owned consistency contract is exercised with the synthetic
fixture `examples/atlas-release-014-consistency.json`. It describes one
aggregate record as three representations (static text, a machine-readable
package row, and an API response) and requires all representations to carry the
same `release_fingerprint`, record identifier, evidence status, uncertainty,
quality and missingness value. The fixture is deliberately synthetic and is
not a product release.

An implementation may render or transport these representations differently,
but it must fail closed when any of the following differ: release fingerprint,
record identity, estimate, uncertainty, quality disposition, or missingness.
Missing values remain explicit (`null` plus a reason) and are never coerced to
zero. A consistency receipt should record the fixture hash, schema versions,
candidate commit and whether each representation passed; a receipt marked
`pass` is only a local rehearsal until the upstream scientific and governance
gates are satisfied.

Fallback: if a hosted API is not approved or cannot be independently operated,
the supported v0.8 preparation surface is the immutable static/data-package
pair. The API contract remains documented but inactive, and no hosted endpoint
or beta publication is implied.
