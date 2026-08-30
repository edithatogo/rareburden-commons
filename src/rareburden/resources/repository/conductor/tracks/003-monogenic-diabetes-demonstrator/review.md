# Track 003 dependency review — Monogenic diabetes rare-within-common demonstrator

## Owner-directed review routing — 2026-08-22

Clinical/scientific, patient/community and data-governance/custodian questions are routed to role-separated advisory agents. Their advice must be presented to the repository owner in an owner decision packet with options, trade-offs, contingencies, uncertainty, dissent and stop triggers. Security/engineering approval is routed to the owner as an owner-operated decision. None of these routes creates independent review, community consent, custodian authority or external scientific approval.

**Review date:** 2026-07-27  
**Historical decision:** Blocked pending Tracks 008, 009 and 010

### Review rerun — 2026-08-01

Repository-owned preparation now includes the non-binding
`examples/analyses/monogenic-diabetes-synthetic.yml` fixture and schema test.
The focused synthetic-protocol suite and full project validation pass. This
does not approve RBC-P002, freeze clinical entities or estimands, or permit
empirical or patient-facing use. The blocked disposition is unchanged.

## Findings

- Track 008 is blocked by the unresolved Track 002 and Track 007 review gates.
- Track 009 is planned and depends on Tracks 002 and 008.
- Track 010 is planned and depends on Track 009.
- Track 003 has one completed repository-owned preparation task (the bounded
  synthetic analysis fixture), but still has no approved RBC-P002 estimands,
  entity scope, evidence ledger, or burden-engine contract.

## Disposition

Keep Track 003 **blocked**. Do not freeze clinical entities, estimands, denominators, or numerical analyses until the semantic, parameter-ledger and burden-engine dependencies are complete and the required clinical, patient/community, data-governance and engineering gates are available.

### External reviewer packet

- **Clinical/genetics:** approve entity and phenotype scope, denominator definitions, ascertainment and interpretation limits.
- **Methods:** inspect estimands, mapping, bias/transportability, uncertainty, validation and double-counting controls.
- **Patient/community:** assess framing, harms, equity and acceptable outputs.
- **Evidence required:** signed protocol/decision record, ledger IDs, reproducible synthetic report, independent review comments and dissent disposition.

### Preparation refresh — 2026-08-01

`docs/track-003-rbc-p002-review-packet.md` records the decisions and evidence
needed before activation. It is repository-owned preparation and does not freeze
RBC-P002 or claim clinical, empirical or patient/community approval.

## Dependency and bounded-scope reconciliation — 2026-08-29

Tracks 008, 009 and 010 are now complete within their explicitly bounded
semantic, ledger and synthetic-alpha contracts. The historical dependency
block is closed. Track 003 is Active only for protocol/interface registration
and review preparation.

The v0.2.0 bounded registration binds the exact upstream commit/tree and hashes
for the synthetic semantic scope, ledger profile, burden-engine candidate,
estimand/denominator contract, population-state contract and framing guard. It
does not promote the existing incompatible population-times-fraction fixture.

Still blocked: clinical gene/phenotype freeze, empirical parameter activation,
controlled data, public-aggregate execution, independent review, actual
patient/community authority, publication and production release. The
exact-candidate scientific/methods, engineering and simulated harm agent
reviews passed for candidate `675c38e`, and the repository owner accepted the
bounded registration in
`docs/decisions/2026-08-29-track-003-bounded-registration-disposition.yml`.
These receipts are advisory repository evidence only and create no independent,
clinical or community authority. The next repository-owned gate is qualification
of a protocol-compatible synthetic denominator or exact rights-receipted
public-aggregate parameter set under issue 261; execution remains disabled.

## Current acceptance audit — 2026-08-30

The historical dependency and execution paragraphs above are not current blanket
blockers. One exact synthetic denominator assurance execution was subsequently
authorized and retained under the 2026-08-29 disposition. Its output inventory
does not constitute the complete demonstrator or cover additional executions.

The original specification permits an end-to-end public/synthetic reference
analysis and labelled outcome/cost scenarios. No synthetic-first scope reduction
is necessary. Three advisory lanes confirmed this reading at base `50d8cb9`.
`docs/track-003-full-reference-acceptance-2026-08-30.md` maps every remaining
deliverable and preserves the exact-execution and external-fact boundaries.
The new input builder and bundle implement parameter/definition preparation;
full scenarios, execution, reproduction, report/package and final disposition
remain pending. Track 003 remains Active, not Complete.

## Twelve-scenario implementation — 2026-08-30

The in-memory runner now implements primary, denominator, ascertainment,
carrier/penetrance, forward referral, age, calendar, coverage, unclassified and
stratum-dependence calculations. All 62 focused tests pass. Advisory review
identified and resolved ambiguous conditional summaries at empty populations;
assumed inputs are explicitly named and metric metadata travels with results.
The contract records evidence-family applicability without empirical validation.
Exact panel evidence is in
`docs/reviews/track-003-reference-runner-panel-2026-08-30.yml`.
Retained execution, reproduction, report and final acceptance remain pending.

## Exact package preparation — 2026-08-30

The package manifest binds 74 source/input/environment/interpretation files and
twelve scenarios with seed 20260830 and 10,000 iterations. Report, CSV and JSON
rendering are implemented and tested in memory. The CLI fails closed on pending,
different or stale dispositions, mismatched executed-module roots, changed
decision bytes and pre-retention candidate drift. Three advisory lanes passed
after fixes; the exact file receipt is
`docs/reviews/track-003-reference-package-panel-2026-08-30.yml`.
This is preparation, not an owner execution decision, empirical validation or
completed Track 003. Retained output review, reproduction and final acceptance
remain pending, including explicit adjudication of the noncomparability
disposition for qualified external evidence.
