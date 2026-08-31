# Track 009 dependency review — Evidence and parameter ledger

## Bounded export destination maintenance — 2026-09-01

The export destination guard now rejects all final-path symlinks, including
dangling links. Previously a dangling link was replaced by the export itself;
the missing target was not created. Existing-target links were already rejected.
This is inconsistent destination validation, not a write-through vulnerability.

Three actual role-separated advisory agents reviewed engineering, security and
usability/harm boundaries. Engineering observed one failing regression before
the fix (11 others passed), then all 12 focused tests passed. Security and
usability/harm reviewed the change and preservation coverage without rerunning
those tests. No blocking findings or dissent remained. No actual community
participation, representation, independent review or custodian authority is
claimed. The existing owner direction authorizes this bounded integrity repair.

Reviewed file SHA-256 bindings:

- `src/rareburden/ledger_store.py`:
  `bc16aad6494c926104c8d9b617f24762f975d8cd8a30b3836dff330f4312c6f5`
- `tests/test_ledger_store.py`:
  `e7f8464d9264605af8eb117c7d372fa92ca1121209daac79b31a65e111c735d7`
- `docs/evidence-ledger-009-reference.md`:
  `0d7f3e19869cd2c7b83f1a419784ff0543e6cb4c41b41deb86574fd150a99b0b`

Hosted Windows testing exposed a test-only path-spelling assumption: `readlink`
returns an extended Windows path. The regression now compares the link's value
before and after rejection, without normalizing away a change or requiring a
particular path spelling. All 12 focused tests passed locally after correction;
the production guard is unchanged. The initial full local gate passed 1,776
tests; hosted Windows had 1,774 passes and these two assertion failures before
the correction. Hosted verification of the corrected assertion is separate.

Recommendation: accept the minimal guard repair with preservation regressions;
deferring it leaves inconsistent link handling. Broader filesystem confinement
is a separate design, not a condition silently satisfied here. Ordinary new
exports and intentional regular-file replacement remain supported. Stop if
valid receipt/export bytes change, a link or target is modified on rejection,
or tests indicate unsupported platform behavior. Parent-directory symlinks,
check/replace races and privileged replacement remain limitations. Frozen
contracts and historical evidence are unchanged; bounded completion scope,
empirical fitness, activation and release authority are not extended.

## Bounded store initialization maintenance — 2026-08-31

Reviewed candidate: `7539bc7c4d2400daaee8cad187bd18697f9ce534`, tree
`a41978e2b40a468afbb429c3179866d5e481e21d`. Manifest:
`manifests/ledger/track009-store-integrity-20260831.json`, SHA-256
`f4ce136884bcb11025e19667bb3561e00696200d2b4f2aea8bcdc1322d87ba9d`.
Annotated non-release tag `evidence/track009-store-integrity-2026-08-31` was
pushed; a separate remote clone fetched it and resolved the exact commit/tree.
`git fsck --connectivity-only` passed. Retain this evidence tag during branch
cleanup; shallow/tag-excluding clones must explicitly fetch it.

Regression evidence: nine failures before the fix, all 12 new cases passing
afterward; 21 focused new/existing store tests passed. Root ran
`PYTEST_ADDOPTS='--timeout=120' uv run --no-sync make check`: 1,761 tests and all
repository gates passed. This timeout override is local only; hosted defaults
are unchanged. Freeze and candidate manifests retain their original hashes.
All three agents verified the exact candidate and four manifest hashes and
recommended bounded acceptance without dissent. Security additionally verified
all 15 artifact-hash references in the frozen contract/candidate manifests.

This maintenance preserves the completed synthetic and exactly-receipted
public-aggregate scope. It rejects dangling final-path database symlinks, reports
SQLite connection/initialization failures through `LedgerStoreError`, and closes
an established connection before propagating initialization failures. Valid
storage, schemas, receipt chains, exports and frozen artifacts are unchanged.

The simulated role-separated advisory panel covers engineering, security/data-use
and usability/harm. Owner-executed simulated-community challenge; no actual
community participation, representation, consultation, endorsement, consent or
independent review. The existing owner direction permits bounded repair, not
new custody or release authority.

Recommendation: deliver the constructor-only repair with failing-then-passing
regressions and full validation. Alternative: defer broader filesystem hardening
to a separate scoped review. Remaining risks include parent-directory symlinks,
check/open races, privileged replacement, access control, backup and signed
checkpoints. Stop on changed valid receipt hashes, weakened immutable triggers,
sensitive data or unsupported claims of tamper-proof or custodian-approved storage.

**Review date:** 2026-07-27  
**Decision:** Blocked pending Tracks 002 and 008

## Findings

- Track 002 remains in review pending live-source, licensing, scientific, data-governance and security evidence.
- Track 008 remains blocked pending Tracks 002 and 007.
- No approved Track 009 ledger contract or migration tooling has been completed; existing generic ledger code, fixtures and impact tracing remain preparatory and are not a frozen Track 009 contract.
- Scientific, data-governance and engineering review gates remain required.

The repository-owned impact-tracing gap is now addressed: validated ledgers can
return the sorted parameter IDs affected by changed source-release IDs, with
empty and unknown release sets failing closed to an empty impact list. Focused
ledger tests pass. This does not activate the ledger contract or replace source
and semantic approvals.

### Preparatory implementation rerun — 2026-07-31

The repository now also contains a transactional SQLite reference store for
validated ledger snapshots. It enforces sequential revisions, rejects ordinary
update/delete operations, creates canonical content and chain receipts, verifies
the complete history and exports canonical JSONL atomically. Bounded query,
detached export and explicit population/period compatibility checks have focused
positive and negative coverage.

This is engineering evidence, not an activated or frozen v0.4 contract. Database
ownership is not custodian authority; a privileged file owner can replace the
database or remove triggers. Signed checkpoints, operational access control,
approved migrations, full provenance-link contracts and external review remain
open.

The non-binding parameter contract now also requires parameter revisions,
uncertainty and licence states, transformation and semantic links, and explicit
population/geography and period contexts. A separate assumption schema and
conflict grouping make assumptions and alternative evidence visible without
automatic selection. Ordering, missingness, incompatibility and supersession
failures have focused negative coverage.

Track 002 integration now has an explicit fail-closed source-release link check,
and a deterministic human-readable report separates assumptions from other
evidence while exposing licence, uncertainty, provenance and limitations. This
does not clear Track 002's live-source or rights reviews.

Repository-level compatibility with all three demonstrator specifications is
now exercised by schema-validated, non-binding ledger profiles in
`examples/demonstrators/`. The checker resolves compatible synthetic bindings,
rejects incompatible quantity types and requires every unbound role to state
why it remains unresolved. All three profiles remain `analysis_ready=false`;
this is contract evidence, not scientific, clinical, custodian or governance
approval.

### Review rerun — 2026-07-29

Repository review result: **Pass with dependency blockers**. The impact-tracing
implementation and focused tests are internally consistent, and the full project
validation gate passes. Track 009 remains blocked because Tracks 002 and 008 are
not complete; no ledger contract, migration path or demonstrator validation has
been frozen.

## Disposition

Keep Track 009 **blocked**. Do not freeze evidence-ledger contracts until source acquisition and semantic contracts are formally complete.

### External reviewer packet

- **Epidemiology/methods:** approve parameter identity, estimands, quality/bias/transportability and conflict rules.
- **Data governance:** approve rights, provenance, retention, licence states and restricted-source handling.
- **Engineering:** inspect schema validation, revisions/supersession, export, migration and impact tracing.
- **Evidence required:** validated fixtures, ledger audit, schema/version decision and unresolved-issue disposition.

### External-gate panel synthesis — 2026-08-01

The preparatory panel report (`docs/v1-subagent-panel-report-017.md`) is
technical evidence only; it does not provide epidemiology, custodian or
engineering sign-off. Track 009 remains blocked on Tracks 002 and 008 and the
v0.4 contract and migration path remain unfrozen.

### Preparation refresh — 2026-08-01

`docs/track-009-ledger-review-packet.md` records the required epidemiology,
data-governance, engineering and operational-custody decisions. It is
repository-owned preparation and does not freeze the v0.4 ledger contract.

### Bounded source-ledger review — 2026-08-16

Repository result: **Pass for bounded preparation with three unresolved medium
findings**. Source bindings are fingerprinted to Track 008 and current Track 002
evidence. The ledger rejects private, disabled, unusable-licence and mutable
links, and alternative parameters require explicit selection and rationale.

The role-separated repository challenge is advisory and owner-ready, not an
external epidemiology, custodian or independent approval. Track 008 remains
blocked; therefore Track 009 remains blocked, empirical activation stays false,
and the v0.4 ledger contract is not frozen.

### Freeze-readiness review — 2026-08-21

Repository result: **Pass for closure-contract preparation and issue assignment
only**. The three unresolved medium findings now have stable IDs, accountable
roles, required evidence and fail-closed pending states. The validator binds
activation to completed Tracks 002 and 008 and rejects hidden or unassigned
issues, unsupported resolution, premature approval/freeze claims, panel
independence claims, and freezes lacking exact candidate, ledger-export,
source/semantic/transformation, migration and accountable-decision evidence.
No finding is resolved and no review or freeze authority is inferred.

### Bounded agent-owner review closeout — 2026-08-22

Repository review result: **Pass for bounded synthetic assurance; Track 009
remains blocked and unfrozen**. Track 008 is complete for its exact bounded
provisional non-clinical semantic core, so the Track 009 challenge was rerun
against the current dependency state. The epidemiology/estimand, rights/data-
use and engineering perspectives remain role-separated agent advice, and the
repository owner recorded the disposition in
`docs/decisions/2026-08-22-track-009-agent-owner-closeout.yml`.

The three existing medium findings remain pending: empirical estimand fitness,
source/custodian rights and engineering/release review evidence. No empirical,
controlled, clinical, patient/community, independent-review, contract-freeze,
production or release claim is made. Track 009 stays `blocked`; only the
bounded synthetic preparation lane is retained.

## v0.4 contract freeze disposition — 2026-08-22

**Decision:** Bounded v0.4 contract freeze accepted; Track 009 remains blocked.

- Owner accepted both agent-panel recommendations within their declared
  scopes (`docs/decisions/2026-08-22-track-009-owner-v04-freeze-disposition.yml`).
- Contract surfaces bound in `manifests/ledger/track-009-v0.4-contract-freeze.json`;
  candidate containment unchanged.
- EPI-MED-01 and RIGHTS-01 resolved within declared scope; empirical
  activation of real sources and controlled data remain behind exact-receipt
  gates and outside v0.4 scope.
- Completion is bounded: empirical activation of real sources, controlled
  data and any scope extension remain behind exact-receipt gates and require
  fresh packets and owner dispositions.
- The owner disposition explicitly records `track_complete: false`. It does
  not authorise a Track 009 completion transition, independent review or
  release.

## Bounded track completion — 2026-08-26

**Disposition:** Complete for the bounded synthetic and exactly-receipted
public-aggregate contract scope only.

- The repository owner separately authorized completion in
  `docs/decisions/2026-08-26-track-009-bounded-completion-authorization.yml`,
  bound to candidate commit `2ac13c0` and tree `2b8cc238`.
- `scripts/check_track009_bounded_completion.py` verifies the exact freeze
  manifest and prior freeze disposition, lifecycle records and fail-closed
  authority boundary.
- Empirical parameter activation, controlled-data activation, independent
  review, publication and release authority remain false. Completion does not
  satisfy those external or downstream gates.
