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
- [x] Probe documented concrete World Bank indicator queries and source terms/download routes; record HTTP results and unresolved file/hash selection. Evidence: review record updated 2026-07-27.
- [x] Complete bounded candidate inventory for supported open, API and manual sources, with access class, terms route and next evidence. Evidence: `review.md` inventory v0.1.0, 2026-07-27; exact file/hash selection remains pending.
- [x] Capture a content-addressed World Bank reference-query response. Evidence: 310-byte HTTP 200 response, SHA-256 `cf007aeb8ff4078b46a28861c022c678c22b6c115b255b0f8f0c6ce58de6c5cb`, 2026-07-29; production indicator approval remains open.
- [x] Hash the public Orphadata terms catalogue, UN WPP methodology and WHO data-terms pages. Evidence: hashes and retrieval sizes recorded in `review.md`, 2026-07-29; exact production files and source approval remain open.
- [x] Record the owner-approved candidate scope without activating production acquisition. Evidence: `review.md` scope decision, 2026-07-29.
- [~] Pin exact Orphadata, UN WPP and WHO artifact URLs/releases and record hashes after the approved source pages expose stable download routes. Orphadata endpoints and hashes are recorded in `review.md` (2026-08-01); exact UN WPP/WHO candidate routes and streamed hashes are now recorded there too. `docs/track-002-source-registration-template.md` records the remaining terms, scope and reviewer fields; production activation remains open.
- [x] Bound the approved World Bank query to named geographies and years, then capture a final response manifest. Evidence: explicit `AUS;NZL`, 2000–2021 query, 8,826-byte HTTP 200 response and SHA-256 recorded in `review.md`, 2026-07-29.

## Review fixes — 2026-08-01

- [x] Remove duplicate exact-pin task and reconcile stale unresolved-route
  wording after the UN/WHO candidate hashes were recorded. Evidence: this
  plan and the corrected review section; full `uv run make check` passed.

## Subagent panel preparation — 2026-08-02

- [x] Route repository-owned source, terms and incident review preparation
  through the subagent review-panel policy in
  `docs/subagent-review-panel-policy.md`.
- [ ] Keep scientific and data-governance dispositions as accountable external
  gates; panel findings prepare the packets but do not satisfy those gates.
- [x] Record the panel’s bounded Option A source posture and contingencies in
  `docs/track-002-panel-disposition-2026-08-02.md`; all candidates remain
  inactive pending accountable receipts.
- [x] Record the panel’s bounded governance posture: ephemeral retrieval,
  metadata/hash retention, no raw redistribution, and fail-closed terms or
  checksum drift handling.
- [x] Add a synthetic four-candidate source-change mutation matrix covering
  checksum drift, redaction and non-promotion. Evidence: parametrized CLI
  integration test in `tests/test_cli_integration.py`.

## Single-developer review mode

Repository-owned review tasks use the subagent panel; accountable external
scientific and data-governance gates remain separate and pending.

## Closure plan — 2026-08-02

- [x] Add the dependency-ordered closure plan shared with Track 007 in
  `docs/track-002-007-closure-plan-2026-08-02.md`.
- [ ] Obtain qualifying scientific, custodian and Track 007 challenge receipts;
  until then retain `in_review` and registration-only behavior.
- [x] Encode the approved bounded Option A source scope in
  `docs/track-002-option-a-scope.yml` with WHO/World Bank deferred and
  activation disabled.
- [x] Add the qualifying-evidence sourcing sequence and contingencies in
  `docs/track-002-qualifying-evidence-sourcing-plan-2026-08-02.md`.
- [x] Implement the machine-readable qualifying-evidence request register and
  fail-closed regression test in
  `docs/track-002-qualifying-evidence-request.yml` and
  `tests/test_track_002_evidence_request.py`.
- [x] Add a regression guard for the approved Option A scope and deferred-source
  activation boundary in `tests/test_track_002_option_a_scope.py`.
- [x] Add a fail-closed regression guard for the source-packet checklist and
  pending accountable dispositions in `tests/test_track_002_evidence_request.py`.
- [x] Add a regression guard proving the external-gate receipt template remains
  blank and non-approving in `tests/test_external_gate_receipt_template.py`.
- [x] Add a regression guard keeping deferred UN WPP and WHO manifests
  conditional, candidate-only and pending review in
  `tests/test_track_002_option_a_scope.py`.
