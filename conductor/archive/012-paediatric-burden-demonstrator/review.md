# Track 012 dependency review — Collective paediatric rare-disease burden demonstrator

## Owner reference disposition — 2026-09-06

Under ADR-0005 and ADR-0009, the repository owner (`edithatogo`) recorded the reference
closeout disposition for Track 012 (`docs/decisions/2026-09-06-track-012-owner-reference-disposition.yml`).
Track 012 is marked as **Complete (synthetic reference; no empirical validation)**.
The simulated role-separated advisory panel reviewed the demonstrator outputs across paediatric clinical,
health economics, engineering/security, and simulated community/equity lanes
(`docs/reviews/track-012-reference-output-panel-2026-09-06.yml`), confirming that person-level deduplication,
multimorbidity handling, and Track 004 offline node integration execute deterministically.
Controlled administrative data access, live hospital linkage, and clinical interpretation remain
deferred to post-v1 under ADR-0005.

## Bounded threshold integrity review — 2026-08-31

Reviewed candidate: `c3abd9c586f5999c9f9eae88b486545adc8c382f`, tree
`40e3a24047861c43cde677b0685e35f6396af0a0`. Manifest:
`manifests/demonstrators/track012-threshold-integrity-20260831.json`, SHA-256
`844943e594b8b48fca0c67b8b05a5c9c9a261c1f8d29dc86aeed5f019f3e6594`.
Annotated non-release evidence tag
`evidence/track012-threshold-integrity-2026-08-31` was pushed and its remote
peeled commit verified, preserving the candidate across squash and branch cleanup.

Regression evidence: eight failures before the guard, all 17 new cases passing
after it; 31 focused new/existing cases passed. Root ran
`PYTEST_ADDOPTS='--timeout=120' uv run --no-sync make check`: 1,749 tests passed
with all repository gates. The timeout override is local only. Fixture, receipt,
dependency bindings and all six bound dependency hashes remain unchanged.
All three advisory agents verified the exact candidate and five manifest hashes
and recommended bounded acceptance without dissent; security also verified the
six dependency hashes. Tag publication was subsequently verified by root.

This maintenance tranche enforces the existing integer-at-least-two input
contract before linked-table processing. It introduces no threshold policy,
controlled-data pathway, clinical/economic estimand or new retained analysis.
The existing floor is a synthetic reference-program constraint, not evidence
that two is safe or approved by any custodian.

Current review routing follows ADR-0009 and the simulated role-separated
advisory panel policy. Engineering, security/data-use and usability/harm
perspectives challenge the repair. Owner-executed simulated-community challenge;
no actual community participation, representation, consultation, endorsement,
consent or independent review.

Recommendation: deliver the bounded type-check repair under the owner's existing
implementation direction, conditional on rejection tests and unchanged valid
receipt evidence. The alternative is to defer broader disclosure work until
actual policy and methods evidence exists. Site-specific inferential risk,
stakeholder needs and deployment permissions remain unresolved. Stop on changed
valid output, reduced thresholds, sensitive input or expanded activation claims.

Track 012 remains **blocked** on its original requirements. Older dependency
statements below are historical: Tracks 008–010 now have bounded completion,
which does not supply the missing Track 004/005 or paediatric requirements.

**Review date:** 2026-07-27  
**Decision:** Blocked pending Tracks 004, 005, 008, 009 and 010

## Findings

- Tracks 004 and 005 are blocked, and Tracks 008, 009 and 010 are also blocked.
- No approved paediatric protocol, data pathway, synthetic linked-data model, federated integration or disclosure package has been completed; only a non-binding protocol draft exists.
- Paediatric, clinical, economic, privacy, data-governance, security and patient/community gates remain required.

Repository-owned preparatory work now includes an entirely synthetic linked-data
fixture covering person, diagnosis, admission, death and cost tables, with
multimorbidity retention, duplicate-admission handling and disclosure-boundary
rules. It contains no real or controlled data.

### Review rerun — 2026-07-29

Repository review result: **Pass with dependency and governance gates**. The
fixture and reference documentation are bounded and reproducible, and the full
validation gate passes. Track 012 remains blocked pending Tracks 004, 005,
008–010 and paediatric, privacy, Indigenous/data-governance, security,
patient/family and engineering review.

## Disposition

Keep Track 012 **blocked**. Do not activate controlled-data or paediatric burden work until all prerequisite contracts and approvals are available.

### External reviewer packet

- **Paediatric/clinical/economic:** approve estimands, coding, observation windows, utilisation, mortality and cost interpretation.
- **Privacy/data governance/security:** approve custodian pathway, linkage authority, Indigenous governance, suppression, retention and incident controls.
- **Patient/family:** assess acceptable use, equity, language and harms.
- **Evidence required:** approved pathway record, synthetic linked-data run, disclosure tests, export specification, review comments and dissent disposition.

### Preparation refresh — 2026-08-01

`docs/track-012-rbc-p004-review-packet.md` records the decisions and evidence
needed before activation. It is repository-owned preparation and does not
constitute paediatric, privacy, Indigenous/data-governance, security,
engineering or patient/family approval.

### Bounded dependency reconciliation — 2026-08-16

Exact repository-owned artifacts from Tracks 004, 005 and 008–011 are now
bound to an entirely synthetic linkage exercise. The deterministic receipt
deduplicates people, retains multimorbidity, exposes missing mortality and cost
coverage, suppresses jurisdiction cells below the synthetic threshold and
performs no imputation. Negative tests reject activation, broken linkage,
duplicate people and an unsafe threshold.

This resolves repository dependency compatibility only for synthetic
assurance. It supplies no real child-level data, access authority, coding
validation, clinical/economic interpretation, transportability evidence or
policy claim. Panel findings and owner disposition also remain pending. Track
012 therefore remains **blocked**.
