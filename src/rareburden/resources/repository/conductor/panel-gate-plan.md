# Agent-panel and owner gate plan

**Status:** current under ADR-0009; agents advise and the repository owner
records the accountable disposition.

## Scope and boundary

The single-developer repository routes evidence assembly, challenge and draft
recommendations to panels of role-separated agents. The repository owner is
the accountable methods, data-use, operations and release decision-maker.
Agent-panel work is advisory and is never described as independent review.
Panels must not impersonate or self-appoint a human, constituted-community,
custodian, licensor, institutional or external authority.

Publisher licences, third-party rights, registry events and any future
controlled-data custodian policy remain evidence-bound facts. A bounded
public/synthetic release excludes claims that require facts or permissions that
are unavailable.

## Options

### Option A — one cross-track panel programme (recommended)

Use at least three agents per packet: methods/clinical, governance/security,
and patient/community/usability. Add a release/reproducibility specialist for
Tracks 014–017. Bind each output to a commit and evidence-manifest digest,
record dissent, and emit an exact owner-disposition packet. Emit an external
fact request only when a publisher, registry or future controlled-data scope
actually requires it. This is the most consistent and lowest-overhead option.

### Option B — specialist panels per gate

Run separate scientific/clinical, community/harm, rights/data-use, operator and
release agent panels. This gives deeper challenge but duplicates evidence
handling and increases coordination and drift risk.

### Option C — panel-only closure

Allow panels to mark gates accepted without an attributable owner disposition.
This is rejected: it would erase accountability and violate the fail-closed
release contract.

## Recommendation and contingencies

Proceed with Option A. If a panel cannot reach a coherent recommendation,
preserve dissent and require the owner to narrow, revise, defer or stop. If a
required rights or custodian fact is unavailable, narrow or disable the affected
claim. If an actual custodian policy imposes stricter terms, those terms
override panel recommendations. Owner-operated reproduction remains qualifying
repository evidence and is labelled non-independent.

## Accepted downstream preparation disposition — 2026-08-20

The repository owner accepted Option B for downstream execution: reversible,
clearly labelled synthetic preparation and cross-cutting security engineering
may proceed while the freeze order remains Track 008, then Track 009, then
Track 010. This is separate from the panel-organisation options above.

The machine-enforced plan is
`../docs/downstream-bounded-preparation-plan-2026-08-03.yml`, and the owner
record is
`../docs/decisions/2026-08-20-owner-option-b-bounded-preparation.md`. Human or
community authority, custodian, clinical, independent-review, quality,
archival and release gates remain blocked. Owner disposition is owner-operated
governance, not independent review.

## Gate matrix

| Gate | Panel work | Accountable disposition or fact | Fail-closed action |
|---|---|---|---|
| Scientific/clinical | Check estimands, mappings, bias, uncertainty, clinical interpretation and dissent | exact-candidate owner disposition | remove or bound unsupported metric/claim |
| Community/harm | Challenge relevance, acceptable use, harms, equity and framing | agent recommendation and owner disposition; no constituted-community claim | remove affected use or stop publication |
| Rights/data-use | Check terms, redistribution, retention, withdrawal and disclosure | owner disposition plus exact publisher/custodian facts where applicable | disable source, node or redistribution path |
| Operator/reproduction | Test public instructions, clean install, workflow and equivalence | owner-operated exact-candidate receipt | mark reproduction unavailable/failed |
| Release | Check evidence index, provenance, support, corrections and exclusions | repository-owner release/bounded/revise/stop decision | no stable tag or publication |

## Dependency-ordered workflow

1. Freeze the candidate commit and evidence manifest.
2. Run the relevant panel and record role, scope, findings, dissent and digest.
3. Produce an owner-disposition packet containing exact decision questions and
   evidence; separately identify any required external fact.
4. Keep the gate pending until the owner disposition and every applicable fact
   are attached.
5. Apply panel-recommended repository fixes where in scope; rerun validation.
6. Reconcile cross-track decisions in the v1 evidence index.
7. Release only after every blocking gate has a disposition or the claim is
   explicitly bounded out of scope.

## Machine-traceability requirements

Every panel packet records `track_id`, reviewed commit, evidence-manifest hash,
panel roles, timestamp, findings, dissent, recommendation, unresolved gates and
the requested accountable receipt. No credentials, personal data or raw
restricted material may be included.

The machine-readable contract is
`schemas/panel-review-packet.schema.json`; the accompanying template and
synthetic fixture are preparation aids only.

The current Track 017 contract is
`docs/track-017-evidence-contract-reconciliation-2026-08-20.md`; the older
`docs/external-gate-register-017.md` is retained as a legacy candidate template
and does not add an additional-person gate.
