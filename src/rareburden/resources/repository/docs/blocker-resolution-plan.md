# Blocker-resolution plan — 2026-08-01

This plan sequences repository-owned preparation and external evidence without
activating production acquisition, controlled-data processing or v1 release.
It is a planning artefact, not an approval or a status transition.

## Decision order

1. **Track 002 source authority (current v0.3 gate).** Pin one exact
   Orphadata pair (already recorded), one UN WPP file and one WHO aggregate
   file. For each, retain URL, publisher release/version, retrieval timestamp,
   SHA-256, MIME/size, licence/terms, attribution, redistribution position and
   intended-use disposition. Obtain scientific and data-governance decisions
   against those exact records. Keep adapters in registration/probe mode until
   all fields are present.
2. **Track 007 review authority (parallel v0.3 gate).** Freeze
   `RBC-LAND-007` search strings and eligibility rules, register the protocol
   where the chosen service permits, rerun GitHub/Zenodo/OSF/Hugging Face
   searches, preserve raw metadata and timestamps, screen/deduplicate with
   reasons, and obtain independent methods plus patient/community challenge.
3. **Track 008 then 009.** Once 002 and 007 are accepted, review semantic
   mapping states and evidence/parameter conflict contracts; unresolved source
   rights or novelty claims remain blockers.
4. **Track 010 then 003/004/005/011/012.** Implement and validate the burden
   engine before demonstrators or federated-node activation. Use only synthetic
   fixtures until scientific, custodian and community gates clear.
5. **Track 013, then 014/015/016, then 017.** Preserve the dependency graph;
   do not treat local tests or subagent panels as independent approval.

## Recommended evidence route and contingencies

| Gate | Recommended route | Safe fallback | Stop condition |
|---|---|---|---|
| UN WPP exact file | Use the publisher-provided WPP 2024 workbook URL from its current download page; hash the selected workbook and record variant/geography/year scope. | Manual registration packet containing the page capture, filename, terms and custodian-provided checksum. | No stable publisher route or unclear redistribution terms: leave source unactivated. |
| WHO exact file | Select one aggregate GHE release and file from the publisher download route; exclude credited third-party fields unless separately cleared. | Manual registration of the exact file and a terms decision with a bounded non-redistribution cache policy. | Dynamic route cannot produce a verifiable file/terms record: no production adapter. |
| Track 002 review | Named scientific and data-governance reviewers sign the hash-bound source records. | Record a formal revise/bounded decision that narrows supported sources. | No accountable decision: remain in review. |
| Track 007 registration | Register `RBC-LAND-007 v0.1.0` with a public protocol identifier and preserve the submitted snapshot. | Publish the versioned protocol and dated search logs locally while registration is unavailable; do not call it registered. | No protocol identifier and no independent challenge: no final novelty claim. |
| Independent challenge | Obtain an independent methods review and patient/community interpretation/harm review. | Record bounded dissent or revise disposition and narrow claims. | No accountable reviewer evidence: retain provisional decision only. |

## Repository-owned work that can proceed now

- Keep source descriptors, manifests, schemas, redaction and fail-closed
  incident paths tested with synthetic fixtures.
- Keep search logs, raw metadata, deduplication keys, exclusions and claim-to-
  source mappings versioned without declaring completeness.
- Prepare downstream contracts and review packets, but do not change blocked
  track status or activate production pathways.

## Evidence package checklist

Each gate packet must contain: exact artefact or query, source/version,
retrieval event, bytes/MIME and SHA-256, rights/terms and attribution,
transformation, reviewer role and decision, limitations, and a link from the
track review. Credentials, controlled data and raw participant records are
never evidence artefacts in this repository.
