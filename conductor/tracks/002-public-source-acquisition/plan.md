# Track 002 plan

## Phase 1 — Source contracts and schemas

- [ ] Reverify access URLs, terms, release conventions and redistribution conditions. `[M-07, M-08, M-10]`
- [ ] Select exact first files/endpoints and define normalised output contracts. `[M-03, M-09]`
- [ ] Add source-release and acquisition-manifest schemas. `[M-11, M-18, M-20]`
- [ ] Extend geography, representativeness and verification fields in the source catalogue. `[M-07]`

## Phase 2 — Common acquisition framework

- [ ] Implement adapter and manual-registration protocols. `[S-03]`
- [ ] Implement cache, checksum, retry, timeout and atomic-write behaviour. `[M-11, M-20]`
- [ ] Add structured logs that exclude secrets and participant data. `[M-13, M-15]`
- [ ] Add source-change and licence-uncertainty failure modes. `[M-22]`

## Phase 3 — Source adapters

- [ ] Implement Orphadata acquisition and metadata extraction. `[S-01, S-03]`
- [ ] Implement UN WPP acquisition and population normalisation. `[S-03, S-04]`
- [ ] Implement one selected WHO bulk-source adapter or registrar. `[S-03]`
- [ ] Implement World Bank Indicators query adapter with cached responses. `[S-03]`
- [ ] Specify manual IHME and OECD release registration without automating restricted flows. `[M-10]`

## Phase 4 — Normalisation and lineage

- [ ] Implement common geography, age, sex, measure, metric and unit fields. `[M-03, M-11]`
- [ ] Link every transformed row to source and acquisition manifests. `[M-20]`
- [ ] Add lawful/synthetic fixtures and offline integration tests. `[M-19]`
- [ ] Run an end-to-end acquisition-to-normalised-table example. `[S-04]`

## Phase 5 — Review and release

- [ ] Complete licence, scientific, engineering and security review.
- [ ] Verify both Git clone and clean source archive workflows.
- [ ] Add review findings and close or assign every issue.
- [ ] Release v0.3.0 only when Track 007 also satisfies its gate.
