# Track 002 plan

## Phase 1 — Source contracts and schemas

- [ ] Reverify live access URLs, terms, release conventions and redistribution conditions. `[M-07, M-08, M-10]`
- [ ] Select and evidence exact production files/endpoints for each supported live source. `[M-03, M-09]`
- [x] Add source-release, acquisition-manifest and normalisation-manifest schemas. `[M-11, M-18, M-20]`
- [x] Extend geography, representativeness and verification fields in the source catalogue. `[M-07]`

## Phase 2 — Common acquisition framework

- [x] Implement adapter and manual-registration protocols. `[S-03]`
- [x] Implement cache, checksum, retry, timeout, bounded-size and atomic-write behaviour. `[M-11, M-20]`
- [x] Add structured provenance that excludes credentials and participant data. `[M-13, M-15]`
- [~] Complete licence-uncertainty policy and live source-change exercises. `[M-22]` Local policy and pre-network enforcement completed in `c5e50b2`; schema-valid source-change incident evidence completed in `97421ca`; dated live-source exercises remain open.

## Phase 3 — Source adapters

- [x] Implement bounded Orphadata XML extraction against lawful synthetic fixtures. `[S-01, S-03]`
- [x] Implement UN-style population acquisition/registration and normalisation. `[S-03, S-04]`
- [x] Implement a WHO-style aggregate CSV registrar and normaliser. `[S-03]`
- [x] Implement World Bank Indicators canonical query construction and response normalisation. `[S-03]`
- [x] Preserve manual IHME and OECD release registration without circumventing restricted flows. `[M-10]`

## Phase 4 — Normalisation and lineage

- [x] Implement common geography, age, sex, measure, metric and unit fields. `[M-03, M-11]`
- [x] Link every transformed row to source and acquisition manifests. `[M-20]`
- [x] Add lawful synthetic fixtures and offline integration tests. `[M-19]`
- [x] Run an end-to-end acquisition-to-normalised-release example. `[S-04]`

## Phase 5 — Review and release

- [x] Complete internal engineering and security review of the offline substrate.
- [ ] Complete live-source licence, scientific and data-governance review.
- [x] Verify the final exact Git clone, installed wheel and clean source archive workflows. Evidence: `39a4b4d`; clean single-branch clone passed `make check`, and independently installed wheel and source archive both passed `rareburden validate-programme`.
- [ ] Close or assign every external review finding.
- [ ] Release v0.3.0 only when Track 007 also satisfies its gate.

## Review fixes — 2026-07-27

- [x] Refresh internal harness evidence and separate repository validation from live-source and governance gates. Evidence: `506ce6b`.
- [x] Run a bounded dated reachability check for catalog access URLs; record the World Bank root 404 as an endpoint-contract finding. Evidence: `3a62e38`.
- [x] Record dated public access/licence evidence for Orphadata, MONDO, UN WPP, WHO GHE and World Bank API documentation. Evidence: review record updated 2026-07-27; exact production endpoint and governance gates remain open.
