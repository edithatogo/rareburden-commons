# External-gate panel preparation plan

**Status:** preparation only; no accountable gate is discharged by agents.

## Scope and boundary

The single-developer repository routes evidence assembly, challenge, and draft
recommendations to panels of role-separated agents. Agent-panel work is
advisory and is never described as independent review. This replaces internal
reviewer logistics, not the accountable authority required by the acceptance
criteria. Panels must not impersonate or self-appoint a scientific/clinical
reviewer, patient/community authority, custodian, independent operator, or
release authority.

## Options

### Option A — one cross-track panel programme (recommended)

Use at least three subagents per packet: methods/clinical, governance/security,
and patient/community/usability. Add a release/reproducibility specialist for
Tracks 014–017. Bind each output to a commit and evidence-manifest digest,
record dissent, and emit an exact external receipt request. This is the most
consistent and lowest-overhead option.

### Option B — specialist panels per gate

Run separate scientific/clinical, patient/community, custodian, operator and
release panels. This gives deeper challenge but duplicates evidence handling and
increases coordination and drift risk.

### Option C — panel-only closure

Allow panels to mark gates accepted. This is rejected: it would make local agent
outputs appear to be accountable external authority and would violate the
project's fail-closed release contract.

## Recommendation and contingencies

Proceed with Option A. If a panel cannot reach a coherent recommendation,
preserve dissent and mark the gate unresolved. If an external receipt is
unavailable, narrow or disable the affected claim and keep the track blocked.
If a custodian or community authority imposes stricter terms, those terms
override panel recommendations. If no independent operator is available, retain
only repository-owned reproducibility evidence and do not claim independence.

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

| Gate | Panel work | Required accountable receipt | Fail-closed action |
|---|---|---|---|
| Scientific/clinical | Check estimands, mappings, bias, uncertainty, clinical interpretation and dissent | attributable scientific/clinical disposition | remove or bound unsupported metric/claim |
| Patient/community | Challenge relevance, acceptable use, harms, equity and framing | constituted patient/community decision | remove affected use or stop publication |
| Custodian/data-governance | Check terms, redistribution, retention, withdrawal and disclosure | custodian/data-governance terms and conditions | disable source, node or redistribution path |
| Independent operator | Test public instructions, clean install, workflow and equivalence | independent operator receipt | mark reproduction unavailable/failed |
| Release authority | Check evidence index, provenance, support, corrections and exclusions | release/bounded/revise/stop decision | no stable tag or publication |

## Dependency-ordered workflow

1. Freeze the candidate commit and evidence manifest.
2. Run the relevant panel and record role, scope, findings, dissent and digest.
3. Produce a receipt request containing exact decision questions and evidence.
4. Keep the accountable gate pending until a qualifying receipt is attached.
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

The Track 017 register at `docs/external-gate-register-017.md` is guarded by a
regression test and must remain pending until qualifying receipts are attached.
