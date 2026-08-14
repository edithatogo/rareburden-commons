# Delivery workflow

RareBurden Commons follows the Conductor lifecycle:

> **Context → Specification and plan → Implementation → Review → Release evidence**

The same artefact contract applies whether work is driven by a Conductor plugin, another agent or human contributors.

## 1. Work unit

Every material feature, source adapter, demonstrator, governance package or protocol revision is a **track** containing:

- `spec.md` — objective, scope, outputs, acceptance criteria, non-goals and v1 contribution;
- `plan.md` — phases, tasks, requirement links and verification;
- `metadata.json` — status, priority, target release, owner role, dependencies and review gates;
- `review.md` — required before a track is Complete.

`conductor/roadmap.yml` is the normative release plan. `conductor/tracks.md` is the human-readable register.

## 2. Track lifecycle

1. **Planned:** specified but dependencies or entry conditions remain open.
2. **Ready:** dependencies are satisfied and an accountable role can start.
3. **Active:** implementation is progressing through focused tasks and commits.
4. **Blocked:** a documented dependency, approval, risk or finding prevents progress.
5. **In review:** implementation tasks are complete and formal review is running.
6. **Complete:** acceptance and review gates pass; evidence is linked.
7. **Archived:** stopped or superseded without deleting history.

The roadmap validator rejects unknown dependencies, cycles, release mismatches, missing track files and completed tracks with unchecked tasks or no review.

## 3. Branch and commit strategy

- Protect `main` once hosted.
- Use short-lived branches named `track/<id>-<slug>`.
- Make focused Conventional Commits: `docs:`, `feat:`, `fix:`, `test:`, `chore:`, `refactor:`.
- Update the track plan and evidence in the same commit as the work it records.
- Preserve significant methodological history rather than squashing away decisions.
- Merge only when applicable automated checks and review gates pass.

## 4. Definition of ready

A track may enter Ready only when:

1. objective, scope, non-goals and acceptance criteria are explicit;
2. dependencies and external approvals are identified;
3. an accountable owner role and risk owners exist;
4. inputs, outputs, privacy class and licence implications are known;
5. review gates are proportionate to risk;
6. the target release has valid entry conditions.

A named individual need not appear publicly, but the programme must know who holds the role before activation.

## 5. Definition of done

A track is Complete only when:

1. every acceptance criterion has objective evidence;
2. every required plan task is checked or formally removed through scope change;
3. automated tests and quality checks pass where applicable;
4. provenance, uncertainty, limitations, licensing and privacy implications are documented;
5. no sensitive or prohibited data are present;
6. `review.md` records findings, fixes, residual risks and disposition;
7. metadata, register and release evidence are updated;
8. focused Git history records the implementation.

Documentation describing a future capability is not implementation evidence for that capability.

## 6. Research workflow

1. Register the question and estimand.
2. Freeze disease, coding and aggregation definitions.
3. Register eligible source releases and access conditions.
4. Extract or derive evidence and parameters with provenance.
5. Assess bias, representativeness, transportability, overlap and uncertainty.
6. Run primary, sensitivity and structural analyses.
7. Validate with independent sources, implementations and domain/community review.
8. Apply local disclosure and data-governance review.
9. Release code, lawful aggregate inputs, metadata, diagnostics and reproducible outputs.
10. Monitor, correct and supersede without rewriting history.

## 7. Review gates

Repository-owned review preparation uses the [subagent review-panel policy](../docs/subagent-review-panel-policy.md): panels draft findings and test evidence completeness. They do not replace accountable external authorities.

- **Scientific:** estimand, definition, mapping, bias, uncertainty, validation and double counting.
- **Data governance:** terms, authority, custodian conditions, disclosure and withdrawal.
- **Patient/community:** relevance, acceptable use, equity, harms, interpretation and framing.
- **Engineering:** correctness, tests, compatibility, performance, reproducibility and maintainability.
- **Security:** threats, dependencies, secrets, logs, supply chain, incidents and recovery.
- **Programme:** scope, resourcing, partner claims and sustainability.
- **Release:** traceability, evidence pack, support, corrections and bounded claims.

A release is blocked when an assigned gate records an unresolved critical finding.

## 8. Release control

- Milestones are gate-driven, not date-driven.
- Every track has one primary target release.
- A release cannot use Planned, Active, Blocked or In-review work as completed evidence.
- Scientific-validity, privacy, data-rights, community-legitimacy and critical security failures cannot be waived for convenience.
- A bounded exception must remove or narrow the unsupported capability and record an owner.
- v1 decisions use `docs/v1-acceptance-criteria.md`.

## 9. Change control

Material changes to product scope, disease inclusion, burden definitions, ontology relations, primary estimands, economic perspective, privacy boundary, supported interfaces or release gates require a decision record in `docs/decisions/`.

Changes to `conductor/roadmap.yml`, dependencies or blocking v1 criteria use the
single-developer subagent review panel described in
`docs/decisions/ADR-0008-single-developer-review-mode.md`. Any genuinely
external scientific, patient/community, data-governance, security, operator or
release-authority gate remains separately required where the acceptance
criteria call for it.
