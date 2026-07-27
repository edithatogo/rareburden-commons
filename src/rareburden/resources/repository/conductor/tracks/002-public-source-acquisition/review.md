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

## Open blocking evidence

- Verify each live endpoint and current terms with dated evidence.
- Record redistribution and archival permissions source by source.
- Obtain data-governance and scientific review of production source choices.
- Exercise live source-change and licence-uncertainty incident paths.
- Validate final installed-wheel and source-archive workflows in the exact locked environment.

## Disposition

Keep Track 002 **In review**. The substrate may be extended, tested and used with synthetic or explicitly lawful fixtures. Do not call the track complete or issue v0.3.0 until the live-source and governance gates are evidenced.
