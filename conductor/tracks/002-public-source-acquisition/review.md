# Track 002 internal review — Public-source acquisition

**Review date:** 2026-07-27  
**Decision:** Internal implementation passes for autonomous handoff; production/live-source approval remains open

## Passed internal evidence

- Network access is opt-in and bounded by HTTPS, host, address, size, timeout and redirect controls.
- Expected checksums are required by default and changed bytes fail closed.
- Manual registration supports sources whose terms or interfaces should not be automated.
- Acquisition URLs are credential-redacted before provenance is written.
- Source-release, acquisition and normalisation records are content-addressed.
- Synthetic adapters cover Orphadata-style XML, UN-style population CSV, WHO-style aggregate CSV and World Bank responses.
- Normalised rows retain source-release, acquisition and transformation lineage.
- The synthetic reference workflow executes offline and its release passes independent verification.
- Commit `39a4b4d` passed the complete local harness with 265 tests, 90.36% branch coverage and all 15 critical-module floors.
- A clean single-branch clone of `track/002-release-harness` passed `uv sync --frozen --extra dev` and `make check`; distributions built from that clone were installed into separate empty environments, where both the wheel and source archive passed `rareburden validate-programme`.
- Commit `c5e50b2` aligns CLI licence states with the source-release schema, requires evidence or rationale appropriate to each state, and rejects unknown or restricted rights before automated network acquisition. The policy is internally verified only; live terms and source-change exercises remain open.
- Commit `97421ca` adds a schema-valid, credential-redacted `review_required` incident record for pinned checksum changes. Failed downloads still commit no source bytes or acquisition manifest; live-source exercise evidence remains open.

## Open blocking evidence

- Verify each live endpoint and current terms with dated evidence.
- Record redistribution and archival permissions source by source.
- Obtain data-governance and scientific review of production source choices.
- Exercise live source-change and licence-uncertainty incident paths.

## Disposition

Keep Track 002 **In review**. The substrate may be extended, tested and used with synthetic or explicitly lawful fixtures. Do not call the track complete or issue v0.3.0 until the live-source and governance gates are evidenced.
