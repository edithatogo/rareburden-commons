# Track 015 plan

> Repository-owned review uses the subagent panel under ADR-0008; constituted governance and patient/community authority remain separate.

## Phase 1 — Constitute governance

- [ ] Draft and approve body charters, appointment and voting rules. `[M-16]`
- [ ] Establish community/harm agent-panel remit, dissent rules and owner decision rights.
- [ ] Establish methods, rights/data-use and node agent-panel review roles.
- [ ] Publish conflicts, minutes and reserved-decision process. `[M-17]`

## Phase 2 — Operating policies

- [ ] Approve acceptable-use, harm, benefit-sharing and corrections policies.
- [ ] Approve authorship, complaints, appeals and funder-independence policies.
- [ ] Implement Indigenous Data Sovereignty and CARE-aligned node terms.
- [ ] Create country-node agreement and accreditation process.

## Phase 3 — Partnerships and funding

- [ ] Complete adjacency-informed partner and funder map.
- [ ] Write tailored IHME, WHO, Orphanet, RDI, WEF and genomic-programme notes.
- [ ] Define the minimum additional data/method ask for each custodian.
- [ ] Prepare institutional-host and costed sustainability options.

## Phase 4 — Policy translation

- [x] Define policy-product claim boundaries and relationship-state crosswalk. `[C-09]` Evidence: `docs/governance-015-reference.md`; indicator approval remains open.
- [ ] Test framing with community/harm and policy-user perspective agents.
- [x] Define confirmed/proposed relationship register states. Evidence: relationship claim-state contract in `docs/governance-015-reference.md`; no relationships are confirmed.
- [ ] Approve geographic and “global” claims for v1 scope.

## Phase 5 — Review

- [ ] Conduct governance tabletop exercise.
- [ ] Close or bound every blocking governance finding.
- [ ] Record v1 governance readiness decision.

## Preparatory dependency review — 2026-07-29

- [x] Document proposed decision bodies, reserved authority, claim states and
  policy-translation limits without activating governance or partnership claims.
  Evidence: `docs/governance-015-reference.md` and review record.

## Repository-owned preparation — 2026-08-01

- [x] Provide a machine-readable-by-convention decision-register template with
  claim-state, authority, conflicts, remuneration, evidence, correction and
  bounded-fallback fields. Evidence: `docs/governance-015-decision-register-template.md`.
- [x] Provide a non-binding tabletop exercise protocol covering withdrawal,
  global-claim pressure, funder independence, stigmatizing language and
  disclosure risk. Evidence: `docs/governance-015-tabletop-template.md`.
- [ ] Run an authorised governance tabletop and record decisions; external
  facilitator, patient/community authority and governance appointments remain
  required.

## Preparation refresh — 2026-08-01

- [x] Prepared `docs/track-015-governance-review-packet.md` with exact
  constitution, patient/community, custodian, scientific-independence and
  relationship evidence requirements.
- [ ] Keep governance, partnership and endorsement states unactivated until
  constituted dispositions are recorded.

## Bounded repository reconciliation — 2026-08-16

- [x] Implement the single-owner plus role-separated advisory agent-panel
  operating model without claiming independent, patient/community, custodian,
  Indigenous, institutional or partner authority. Evidence:
  `manifests/governance/track-015-bounded-reconciliation-2026-08-16.json`.
- [x] Bind exact Track 007/013, source-rights, archive-capacity and ADR-0009
  evidence; keep the Track 014 release-surface dependency pending until its
  dependency-safe merge.
- [x] Encode relationship claim states, source/rights boundaries and exact
  correction/withdrawal triggers with negative overclaim, evidence-drift and
  dependency tests. Evidence: `scripts/check_track015_bounded_governance.py`
  and `tests/test_track015_bounded_governance.py`.
- [x] Bind the exact merged Track 014 release-surface artifact at merge
  `22388a74e2d8f2c4ff1d59f828279ffabad3b5a7` and SHA-256
  `dd2e97dc8be451144ca2c865afaf96e2b720dcf34a4b3020c55504ce3f887dc0`,
  then re-run the full gate before integration.
