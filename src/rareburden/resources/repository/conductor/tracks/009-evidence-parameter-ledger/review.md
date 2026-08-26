# Track 009 dependency review — Evidence and parameter ledger

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
