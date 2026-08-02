# Subagent review-panel policy

## Default

For every Conductor track, repository-owned review preparation is performed by
a panel of independent subagents. The panel may inspect the specification and
diff, run tests, challenge assumptions, produce dissent, draft dispositions,
and identify missing evidence. Panel outputs are recorded as preparation
evidence and linked from the relevant track review.

## Panel composition

Use at least three perspectives when the track has material scientific,
governance, security or release risk: methods/technical, data-governance or
security, and patient/community or usability. Record each panel role, scope,
independence within the repository task, findings, dissent and proposed
contingency.

## Non-substitutable gates

The panel must not be described as, or used to replace, an accountable
scientific reviewer, constituted patient/community authority, data custodian,
independent operator, named operational owner, or release authority when the
track or v1 acceptance criteria require that role. Those gates remain pending
until a qualifying external receipt is supplied. A panel can prepare the packet
and test its completeness, but cannot self-authorise the gate.

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
