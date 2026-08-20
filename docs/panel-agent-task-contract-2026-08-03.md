# Panel agent task contract

Use this contract whenever a panel is the only available review mechanism.

## Inputs supplied to every agent

- candidate tag/commit: `candidate-2026-08-03`;
- manifest: `rel-b213c531a6b754940f80ab70`;
- input-manifest SHA-256:
  `d3aafd7367609050d6a4c9926a8ddca3013085362f78abd319dd582135612389`;
- exact track, scope, exclusions and question;
- required evidence fields, output schema, deadline and quorum rule.

## Required output

Return role, evidence references, commands or observations, findings,
uncertainty, conflicts, dissent, residual risk, permitted scope, prohibited
claims, contingency and a recommendation. Use `panel_assurance` for status. A
recommendation is not an approval.

For prospective material decisions from 2026-08-21, use the structured
agent-owner decision packet. Supply two or three distinct options, each with
trade-offs, contingencies, rationale and minimum evidence. Preserve uncertainty,
dissent and stop triggers, label every role as a simulated advisory perspective,
and keep the owner disposition separate.

## Prohibited actions

Agents must not invent recipients, claim independence they do not have, send
external requests, include credentials or restricted source bytes, alter the
candidate, or mark an accountable receipt verified.

## Panel synthesis

The orchestrator records each packet separately, reconciles agreement and
dissent, and publishes the narrowest supported recommendation. Claims of
external authority, independent reproduction, community consent, custodian
terms or stable release remain out of scope without a qualifying receipt.
