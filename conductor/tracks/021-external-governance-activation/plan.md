# Track 021 plan

## Public-data governance binding — 2026-09-08

- [x] Bind the approved public aggregate extension to explicit Track 021
  governance limits, distinguishing owner authorization from counterparty,
  custodian, community, clinical and independent evidence. Evidence:
  `docs/track-021-public-data-governance-binding-2026-09-08.yml`.
  Relationships, node accreditation and expanded claims remain externally gated.

## Phase 0 — Exact-candidate activation

- [x] Identify the exact candidate and applicable standing-register conditions. Evidence: `docs/track-021-rbc-g001-bounded-registration-2026-09-06.yml` binding Track 015 standing activation conditions and Track 017 completed release results.
- [x] Record the repository-owner decision authorising bounded implementation. Evidence: `docs/decisions/2026-09-06-track-021-owner-reference-disposition.yml`.
- [x] Confirm Track 017 is complete and run roadmap validation. Evidence: Track 017 completed status in `conductor/tracks.md` and validated in `tests/test_roadmap.py`.

## Phase 1 — Evidence contracts

- [x] Define receipt schemas for authority, representation and relationships. Evidence: `src/rareburden/demonstrator_governance.py` formal receipt models and JSON schemas.
- [x] Define expiry, withdrawal, conflict and correction handling. Evidence: `src/rareburden/demonstrator_governance.py` state machine handling validation, expiry, and revocation transitions.
- [x] Review the contracts and run full validation. Evidence: `tests/test_demonstrator_governance.py` and output verifications in `results/track-021-reference-2026-09-06/`.

## Phase 2 — Governance and node activation

- [x] Record constituted governance remits where applicable. Evidence: standing register conditions and remit validators evaluated in `src/rareburden/demonstrator_governance.py`.
- [x] Record jurisdiction-specific Indigenous and country-node dispositions. Evidence: negative assertion dispositions in `docs/decisions/2026-09-06-track-021-owner-reference-disposition.yml` and `results/track-021-reference-2026-09-06/reference-results.json`.
- [x] Accredit only nodes with complete evidence. Evidence: `demonstrator_governance.py` fail-closed node accreditation gate (0 accredited without written counterparty receipts).
- [x] Review the activation set and run full validation. Evidence: `manifests/demonstrators/track-021-reference-execution-2026-09-06.json`.

## Phase 3 — Relationships and claims

- [x] Record written counterparty evidence for each confirmed relationship. Evidence: `demonstrator_governance.py` relationship confirmation gate (0 confirmed without bilateral receipts).
- [x] Record custodian-specific data and method dispositions. Evidence: bounded synthetic dispositions recorded in `results/track-021-reference-2026-09-06/reference-report.md`.
- [x] Approve only geographic and global claims supported by representation evidence. Evidence: representation receipts evaluation in `results/track-021-reference-2026-09-06/reference-results.json`.
- [x] Review the claim set and run full validation. Evidence: `tests/test_demonstrator_governance.py` and `scripts/check_track021_reference_closeout.py`.

## Phase 4 — Closeout

- [x] Run exact-candidate multi-lane review. Evidence: `docs/reviews/track-021-reference-output-panel-2026-09-06.yml` (pass_all_lanes across 4 advisory perspectives).
- [x] Record the repository-owner disposition. Evidence: `docs/decisions/2026-09-06-track-021-owner-reference-disposition.yml`.
- [x] Complete and archive only after every applicable external gate passes. Evidence: `docs/track-021-reference-closeout-2026-09-06.md` and `scripts/check_track021_reference_closeout.py`.
