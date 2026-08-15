# Track 002 plan

## Phase 1 — Source contracts and schemas

- [x] Reverify the exact bounded candidate URLs, observed terms, release
  conventions, hashes and repository archival dispositions. `[M-07, M-08,
  M-10]` Evidence: `docs/track-002-source-verification-2026-08-15.yml` and
  `docs/track-002-wpp-who-terms-audit-2026-08-15.yml`; accountable source-use
  and production decisions remain separate pending gates.
- [x] Select and evidence exact candidate files/endpoints for every supported
  live-source role. `[M-03, M-09]` Evidence:
  `docs/track-002-source-verification-2026-08-15.yml`; all activation remains
  fail closed pending the per-estimand receipts.
- [x] Add source-release, acquisition-manifest and normalisation-manifest schemas. `[M-11, M-18, M-20]`
- [x] Extend geography, representativeness and verification fields in the source catalogue. `[M-07]`
- [x] Add the source-specific estimand matrix with explicit numerator,
  denominator, metric, geography/year scope and prohibited claims. Evidence:
  `docs/track-002-estimand-matrix.yml`; activation remains conditional.
- [x] Add the coverage and representativeness plan with options and
  contingencies. Evidence:
  `docs/track-002-coverage-representativeness-plan-2026-08-03.md`.
- [x] Add the candidate-bound final extraction specification plan. Evidence:
  `docs/track-002-final-extraction-specification-plan-2026-08-03.md`.
- [x] Instantiate the registration-only extraction specification with exact
  selectors, geography/year filters, transformations and fail-closed rules.
  Evidence: `docs/track-002-final-extraction-specification.yml` and
  `tests/test_track_002_extraction_spec.py`.
- [x] Instantiate the coverage and representativeness matrix for every
  estimand, including missingness, ascertainment, bias and transportability
  limits. Evidence: `docs/track-002-coverage-matrix.yml` and
  `tests/test_track_002_coverage_matrix.py`.

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
- [ ] Complete the live source-change exercise and agent-methods challenge;
  publisher rights remain fail-closed and the owner data-use disposition is
  recorded in `docs/decisions/2026-08-15-public-source-data-use-and-backup-owner.md`.
- [x] Verify the final exact Git clone, installed wheel and clean source archive workflows. Evidence: `39a4b4d`; clean single-branch clone passed `make check`, and independently installed wheel and source archive both passed `rareburden validate-programme`.
- [x] Assign every external review finding to a named gate and bounded
  disposition. Evidence: `docs/track-002-findings-disposition.yml`; assigned
  findings remain open until qualifying receipts exist.
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
- [x] Pin exact Orphadata, UN WPP and WHO artifact URLs/releases and record
  observed hashes. Evidence: `review.md`,
  `docs/track-002-source-verification-2026-08-15.yml` and the source
  registration records; unresolved terms and production activation remain
  separate fail-closed gates.
- [x] Pin the July 2026 Orphadata English epidemiology and alignment XML endpoints and record byte counts and SHA-256 hashes. Evidence: exact endpoint table in `review.md`, 2026-08-01; production activation and reviewer approval remain gated.
- [x] Bound the approved World Bank query to named geographies and years, then capture a final response manifest. Evidence: explicit `AUS;NZL`, 2000–2021 query, 8,826-byte HTTP 200 response and SHA-256 recorded in `review.md`, 2026-07-29.

## Review fixes — 2026-08-01

- [x] Remove duplicate exact-pin task and reconcile stale unresolved-route
  wording after the UN/WHO candidate hashes were recorded. Evidence: this
  plan and the corrected review section; full `uv run make check` passed.

## Subagent panel preparation — 2026-08-02

- [x] Route repository-owned source, terms and incident review preparation
  through the subagent review-panel policy in
  `docs/subagent-review-panel-policy.md`.
- [x] Route methods and data-use review through agent-panel advice and owner
  disposition under ADR-0009; preserve publisher licences and third-party
  rights as immutable evidence constraints.
- [x] Record the panel’s bounded Option A source posture and contingencies in
  `docs/track-002-panel-disposition-2026-08-02.md`; all candidates remain
  inactive pending accountable receipts.
- [x] Record the panel’s bounded governance posture: ephemeral retrieval,
  metadata/hash retention, no raw redistribution, and fail-closed terms or
  checksum drift handling.
- [x] Add a synthetic four-candidate source-change mutation matrix covering
  checksum drift, redaction and non-promotion. Evidence: parametrized CLI
  integration test in `tests/test_cli_integration.py`.
- [x] Record a read-only live reachability probe for the pinned candidate URLs;
  HTTP reachability is explicitly not treated as terms, scientific or
  redistribution approval. Evidence:
  `docs/track-002-live-reachability-probe-2026-08-03.md`.
- [x] Record current public-page terms observations without promoting any
  source or inferring unrestricted rights. Evidence:
  `docs/track-002-public-terms-observation-2026-08-03.md`.

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

## Panel closure planning — 2026-08-02

- [x] Add the joint Track 002/007 panel closure plan with options,
  contingencies and dependency sequence in
  `docs/track-002-007-panel-closure-plan-2026-08-02.md`.
- [x] Prepare a schema-valid synthetic Track 002 panel packet with pending
  scientific and custodian receipts in `examples/fixtures/track-002-panel-packet-synthetic.json`.
- [x] Add a regression guard for exact candidate registration completeness and
  fail-closed pending terms/dispositions in `tests/test_track_002_source_candidates.py`.
- [x] Add a machine-readable source terms/disposition matrix and fail-closed
  regression test in `docs/track-002-source-terms-matrix.yml` and
  `tests/test_track_002_terms_matrix.py`.
- [ ] Obtain separate accountable scientific and custodian/data-governance
  receipts after panel preparation; panels cannot close these gates.
- [x] Add a regression guard proving the external-gate receipt template remains
  blank and non-approving in `tests/test_external_gate_receipt_template.py`.
- [x] Add a regression guard keeping deferred UN WPP and WHO manifests
  conditional, candidate-only and pending review in
  `tests/test_track_002_option_a_scope.py`.
- [x] Implement the per-estimand activation matrix and fail-closed findings
  disposition register. Evidence: `docs/track-002-activation-matrix.yml`,
  `docs/track-002-findings-disposition.yml` and
  `tests/test_track_002_activation_matrix.py`; unresolved custodian and live
  source findings remain non-active.

## Exact retrieval observation refresh — 2026-08-05

- [x] Consolidate the dated endpoint, HTTP, content-type, byte-count and
  streamed SHA-256 observations into
  `docs/track-002-exact-source-observations-2026-08-03.yml`, with explicit
  unavailable-response and terms fail-closed rules.
- [x] Add regression coverage proving hashes are observational only and that
  an unavailable World Bank response cannot be promoted.
- [ ] Re-probe changed or unavailable endpoints and obtain accountable terms,
  scientific and custodian dispositions before activation.

## Exact source and private-archive refresh — 2026-08-15

- [x] Re-probe the exact Orphadata, WPP, WHO GHE and bounded World Bank routes;
  record current page/response hashes, release identities and fail-closed
  archival states in `docs/track-002-source-verification-2026-08-15.yml`.
- [x] Confirm the exact Orphadata product-page evidence: the official July 2026
  epidemiology and alignment pages name `en_product9_prev.xml` and
  `en_product1.xml` respectively and state that all files are CC BY 4.0.
- [x] Prepare the required Orphadata attribution, unchanged-file and
  no-endorsement notice in
  `docs/track-002-orphadata-attribution-2026-08-15.md`.
- [x] Capture the bounded World Bank `AUS;NZL`, 2000–2021 response after the
  earlier unavailable observation; retain it as probe-only and prohibit silent
  WPP substitution.
- [x] Keep WHO bytes absent from Hugging Face until its remaining field-level
  third-party and modification conditions are dispositioned. WPP was archived
  only after exact workbook CC BY 3.0 IGO evidence was recorded; neither source
  is activated by archival.
- [x] Audit the exact WPP workbook notice and WHO dataset terms. Evidence:
  `docs/track-002-wpp-who-terms-audit-2026-08-15.yml`. WPP is CC BY 3.0 IGO
  with attribution and notice preservation; WHO raw Hugging Face upload remains
  withheld pending field-level third-party and modification review. The exact
  WPP workbook is archived at private Hugging Face revision
  `ae188ced2bced5e403e82af61990a28f975f5bc1`.
- [x] Keep production activation and external scientific, patient/community,
  custodian and independent-review claims disabled.

## Aggressive lawful source archival — 2026-08-15

- [x] Classify every current and planned source by dataset type, exact licence
  posture, private/public archive route, GitHub boundary and stop conditions in
  `docs/source-archive-decision-matrix-2026-08-15.yml`.
- [x] Archive the exact bounded World Bank response privately while retaining
  its probe-only, no-WPP-substitution status.
- [x] Archive the exact unmodified WHO GHE workbook privately with withdrawal
  capability; keep public redistribution, derived-field activation and any
  third-party-rights claim disabled.
- [x] Pin MONDO `v2026-08-04`, verify all three canonical artifact hashes
  against publisher-provided SHA-256 digests, and archive the exact artifacts
  privately under CC BY 4.0.
- [x] Keep GitHub as the canonical governance/code/manifest surface and the
  public Hugging Face estate registry metadata-only. Raw public publication is
  source-specific and requires an exact owner release decision.
- [x] Select and pin the exact ClinVar monthly `variant_summary` 2026-08
  snapshot, record its SHA-256 and archive it privately with NCBI/submitter
  attribution and a no-direct-diagnostic-use boundary. Public mirroring remains
  a separate exact release decision.
- [x] Verify the December 2019 PanelApp terms: exact extracts may be retained
  for non-commercial, non-diagnostic research with GEL/contributor attribution,
  but mixed OMIM/Orphanet and output restrictions prohibit a public raw mirror
  without a narrower field-level disposition.
- [x] Capture and privately archive the complete five-page PanelApp current
  panel listing (433 panel/version rows) with a SHA-256 manifest. A first
  full-detail attempt captured 129 records before HTTP 429; do not claim a
  complete detail snapshot and resume only with server-respecting backoff.
- [ ] Complete the remaining PanelApp per-version detail capture using a
  sequential resumable workflow with rate-limit backoff, then bind all 433
  records to a replacement SHA-256 manifest.
- [x] Verify the OECD general terms: data are reusable with attribution unless
  dataset-specific or third-party restrictions apply; acquisition remains
  dataset-specific and metadata-only until an exact OECD dataset is selected.
- [x] Pin the HPO `v2026-06-23` core ontology and annotation artifacts and
  verify all seven publisher digests. Preserve privately, but prohibit a public
  mirror until the embedded HPO terms URL yields an exact accessible terms
  record.
- [x] Record fail-closed archival routes for ICD-10/11, OMIM and SNOMED CT:
  exact licensed editions only, no credential circumvention, and no raw GitHub
  or public Hugging Face redistribution without express rights.
- [ ] Verify exact PanelApp, OECD and any future export-specific terms before
  raw acquisition; default to metadata/hash-only.
- [x] Correct the PanelApp scope from one nominally global source to a
  country-aware registry containing the distinct UK and Australian instances;
  prohibit claims that either instance, or their union, is globally
  representative.
- [x] Audit existing owner infrastructure before creating any archive. Reuse
  `hpo-licensed-ontology-archive` as the canonical mixed-rights terminology
  archive, keep RareBurden's archive project-specific, and record known exact
  duplicate hashes rather than uploading another copy.
- [x] Add UMLS as a candidate terminology-alignment source with public release
  metadata, but keep authenticated artifacts operator-local and public raw
  redistribution prohibited until every selected source vocabulary is
  separately dispositioned.
- [x] Publish the exact rights-filtered Orphadata, Mondo, WPP and bounded World
  Bank payloads to the public Hugging Face dataset
  `edithatogo/rareburden-commons-open-source-snapshots`, bound to commit
  `795150a6b45937228023b97602e6b770ae7f192b`; keep every mixed, unclear,
  authenticated or controlled payload excluded.
- [x] Prohibit export of All of Us Researcher Workbench and Genomics England
  Research Environment controlled data; archive only synthetic code, schemas
  and non-sensitive metadata outside those environments.
