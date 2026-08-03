# Remaining gates plan and panel recommendation — 2026-08-01

This plan was prepared with a technical subagent panel. The panel supplies
structured preparation and contingencies; it is not a constituted scientific,
patient/community, custodian, operator, operational-owner or release-authority
body. No panel output closes an accountable gate.

## Options

### Option A — Recommended: gate-first progression

Close Track 002 and Track 007 evidence packets first, then advance 008 → 009 →
010 and their dependants in roadmap order. Continue repository-owned synthetic
preparation in parallel, but do not activate blocked contracts. This preserves
traceability and minimizes rework.

### Option B — Parallel implementation

Implement downstream code while 002/007 remain unresolved. This can accelerate
engineering exploration, but creates contract drift and cannot produce accepted
release evidence. Use only for isolated synthetic tests and documentation.

### Option C — Scope reset

Cancel or narrow a release and archive blocked tracks. This changes the
programme roadmap and stable-v1 contract; it requires an explicit programme
decision and is not recommended without new evidence.

**Recommendation (approved by repository owner 2026-08-03):** Option A, with Option B limited to non-binding synthetic
fixtures and review packets. Do not choose Option C implicitly.

## Dependency sequence and contingencies

| Order | Track/gate | Repository-owned work | Accountable gate | Safe contingency |
|---:|---|---|---|---|
| 1 | 002 source acquisition | Exact pins, hashes, registration records, fail-closed incidents | Scientific suitability, custodian terms, licensing/redistribution, governance | Synthetic/public fixtures only; exclude unverified source |
| 2 | 007 landscape | Versioned protocol, search logs, screening/exclusions, dedupe | Protocol registration, independent methods, patient/community challenge | Draft adjacency map only; no completeness/novelty claim |
| 3 | 008 semantic | Mapping schemas, ambiguity, hierarchy and version-diff tests | Source/clinical semantics and patient/community naming review | Non-binding contract; no release freeze |
| 4 | 009 ledger | Provenance, conflict, uncertainty, migration and custody tests | Epidemiology, governance and engineering decisions | Synthetic ledger only; no empirical activation |
| 5 | 010 engine | Deterministic estimands, seeded uncertainty, scenarios, safety tests | Scientific/statistical, engineering and patient/community review | Independent-product synthetic mode only |
| 6 | 003/005/011/012 | Synthetic demonstrator profiles, compatibility and negative tests | Clinical, economics, paediatric, community and custodian review | Contract exercises only; no empirical/child/cost claims |
| 7 | 013 validation/equity | Gap schemas, triangulation harnesses, uncertainty and equity fixtures | Independent methods/equity/community review | Bounded gap report; no population equity claim |
| 8 | 014/015 | API/release tests and governance/tabletop packets | Rights/custodian, constituted governance and release decisions | Offline package and draft governance only |
| 9 | 016 operations | Threat model, SBOM, backup/rollback and incident preparation | Independent operator, named primary/backup owners, security/ops acceptance | Maintainer-only preparation; no support promise |
| 10 | 017 stable v1 | Guides, tutorials, evidence index, candidate digest | Independent usability/reproduction and release authority | Public/synthetic candidate only; no v1 tag |

## Receipt contract

Every accountable receipt must identify the role/organisation, independence or
conflicts, exact candidate commit/manifest/digest, evidence and protocol
versions, decision (`pass`, `bounded`, `revise` or `stop`), conditions, dissent,
residual-risk owner, expiry/review date and permitted scope. Missing, expired,
conflicting or digest-mismatched receipts remain pending.

## Immediate autonomous queue

1. Maintain Track 002 and 007 evidence packets and rerun bounded discovery/source
   checks when retrieval dates change.
2. Continue synthetic review packets and negative tests for Tracks 008–012.
3. Keep dependency/status metadata truthful; do not freeze contracts or mark
   tracks complete from local green tests.
4. Re-run the full local validation after each evidence-bearing change and push
   focused commits.

## Implementation checkpoint — 2026-08-03

The executable receipt-collection workflow, gate matrix and contingencies are
in `docs/qualifying-accountable-receipts-plan-2026-08-03.md`.
The candidate-freeze options and decision sequence are in
`docs/frozen-candidate-and-receipts-decision-plan-2026-08-03.md`.
The secure routing and response workflow is in
`docs/receipt-routing-and-response-plan-2026-08-03.md`.
Panel-only operation and agent input/output requirements are defined in
`docs/subagent-review-panel-policy.md` and
`docs/panel-agent-task-contract-2026-08-03.md`.
The completed panel assurance and bounded follow-up options are recorded in
`docs/panel-assurance-report-candidate-2026-08-03.md`.

- [x] Add a machine-readable schema guard for the blank external receipt
  template in `schemas/external-gate-receipt.schema.json` and
  `tests/test_external_gate_receipt_schema.py`.
- [x] Add the non-registering receipt intake validator in
  `scripts/check_external_receipt.py` and
  `tests/test_external_receipt_validator.py`.
- [x] Add the machine-readable pending receipt register and fail-closed
  `qualifying-receipts-check` intake guard.
- [x] Freeze the bounded synthetic-assurance candidate as
  `candidate-2026-08-03` with manifest `rel-b213c531a6b754940f80ab70`.
- [x] Prepare the six digest-bound receipt requests in
  `docs/qualifying-receipt-request-bundle-2026-08-03.yml`; requests remain
  unsent until routed through the agreed secure channels.
- [x] Add the unassigned routing template in
  `docs/receipt-routing-assignment-template-2026-08-03.yml` without inventing
  recipients or channels.
- [ ] Validate and attach qualifying receipts; schema validity alone never
  constitutes an accountable decision.
