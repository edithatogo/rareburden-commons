# Stable v1 release-candidate checklist

**Status:** preparatory; this checklist does not authorize a release.  
**Track:** 017-documentation-adoption-v1  
**Revision:** 2026-08-01

Use this checklist for each candidate. Record the exact commit, environment,
artefact digests, reviewer and decision in the external gate register
(`docs/external-gate-register-017.md`) and linked receipt records. A failed
or unavailable item blocks the candidate unless the unsupported capability is
removed from scope.

## Candidate build

- [ ] Start from a clean clone and frozen lockfile.
- [ ] Verify the supported platform matrix and package metadata.
- [ ] Build source archive, wheel, SBOM, citation metadata and research object.
- [ ] Generate the release manifest from reviewed immutable inputs only.
- [ ] Verify checksums, provenance, licence state and repository identity.
- [ ] Run `uv run make check` and retain the transcript.

## Product and reproducibility

- [ ] Confirm static, package and API outputs share one release fingerprint.
- [ ] Confirm missingness, uncertainty, quality and limitations are visible.
- [ ] Run two clean candidate builds and compare deterministic outputs.
- [ ] Complete an owner-operated clean-environment reproduction with equivalent
      reviewed outputs and label it non-independent.
- [ ] Complete accessibility and documentation-link review.

## Governance and operations

- [ ] Attach role-separated agent-panel recommendations and the exact
      repository-owner disposition without implying unavailable authority.
- [ ] Attach named primary/backup owners and sustainability decision.
- [ ] Verify correction, withdrawal, rollback, backup/restore and incident
      procedures.
- [ ] Record supported scope and every bounded exclusion.

## Fallback disposition

If external evidence is unavailable, mark the candidate `revise` or `bounded`,
do not tag `v1.0.0`, and remove claims requiring the missing evidence. A
owner-operated build is repository evidence, not independent reproduction; a
green local suite is not external governance or publication approval.
