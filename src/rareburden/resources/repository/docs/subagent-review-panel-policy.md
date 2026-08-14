# Subagent review-panel policy

## Default

For every Conductor track, repository-owned review preparation is performed by
a panel of independent subagents. The panel may inspect the specification and
diff, run tests, challenge assumptions, produce dissent, draft dispositions,
and identify missing evidence. Panel outputs are recorded as preparation
evidence and linked from the relevant track review.

## Panel-only assurance mode

When no external participants are available, the repository may operate in
**panel-only assurance mode**. The panel may produce a bounded internal
methods, governance, usability, operations or release recommendation. Every
result must say `panel_assurance`, identify composition and quorum, preserve
dissent, and state what it does not authorize. It may support a bounded
synthetic preview, but must not be relabelled as independent external review,
constituted community consent, custodian authority or stable-release approval.

Each agent task must receive the exact candidate tag/commit, manifest and input
digest, scope and exclusions, question, required evidence fields, output format,
deadline and prohibited actions. Each agent returns findings, references,
uncertainty, conflicts, dissent and a recommendation only.

## Panel composition

Use at least three perspectives when the track has material scientific,
governance, security or release risk: methods/technical, data-governance or
security, and patient/community or usability. Record each panel role, scope,
independence within the repository task, findings, dissent and proposed
contingency.

## Accountable-gate boundary

The panel must not be described as, or used to replace, an accountable
scientific reviewer, constituted patient/community authority, data custodian,
independent operator, named operational owner, or release authority when the
track or v1 acceptance criteria require that role. In panel-only assurance mode,
those gates remain labelled `panel_assurance` and are not claimed as external
authority. A panel can make the best available bounded recommendation and test
completeness, but cannot self-authorise an external gate.

## Track-plan amendment rule

Where a plan says “recruit”, “obtain review”, or “complete review”, interpret the
repository-owned portion as: run the subagent panel, record its draft findings,
and prepare the exact external receipt request. Keep the original accountable
gate task pending unless the project contract explicitly classifies it as
internal engineering review.

## Receipt and fail-closed rules

Panel outputs must be bound to the reviewed commit and evidence manifest. They
must record dissent and unresolved findings. They cannot authorize production
acquisition, controlled-data processing, publication, release, or claims of
independence. Missing or conflicting external receipts keep the track blocked or
in review.
