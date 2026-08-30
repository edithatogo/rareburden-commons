# Track 003 full reference acceptance audit

Status: original-scope implementation in progress, not completion or execution
permission. Audit base: `50d8cb9466c48fbde017010c7db858bdd3cc61be`.

The original and current Track 003 specification permit a public/synthetic
reference dataset and scenario-labelled outcomes and costs. Completing those
deliverables does not inherently require a scope reduction, empirical
activation, clinical approval, controlled data or actual community endorsement.
The earlier suggestion to narrow the milestone to synthetic-first was an
unnecessary inferred gate. It is not adopted as a scope change.

Three role-separated advisory agents (scientific/technical, rights/data-use and
simulated harm) agreed on this interpretation. Their advice does not itself
complete acceptance or supply an execution, publication or release disposition.
The scientific and harm audits retained the exact-execution decision boundary;
the rights audit considered standing owner authorization potentially sufficient
for a new precisely bound disposition. This audit does not adjudicate that
authority question by silently extending the historical receipt.

## Acceptance and implementation map

| Requirement | Current evidence and remaining work |
|---|---|
| Versioned entities and denominator | Bounded registration exists. The new reference input candidate defines fictional diabetes, carrier, expression, detection and unclassified states; these are not clinical definitions. Integration with the execution registration remains pending. |
| Parameter provenance, quality and transport | The reproducible builder creates 18 invented parameter records with content-addressed quality and transport assessments under existing schemas. Each is explicitly assumed. Context identity permits use within the fictional reference only, not empirical transfer. |
| Reproducible primary and sensitivity estimates | One historical assurance output exists. Full candidate runner, deterministic and seeded simulation outputs and separate reproduction remain to be implemented/executed. |
| Population-state distinctions | Report within-diabetes fractions and expected, detected, undetected and unclassified states separately. Total-population prevalence remains unavailable without a compatible registered chain. |
| Outcomes and economics | Inputs cover illustrative diagnosis delay, treatment change, one-year complication probability and direct healthcare cost per case-year. Runner/report must use subgroup-specific hypothetical constructions, not allocate a general burden/cost envelope by case fraction. |
| Uncertainty and structural assumptions | Twelve scenario slots cover denominator, ascertainment, carrier penetrance, referral, age, calendar, model eligibility, unclassified and shared/independent stratum assumptions. These are required outputs, not implemented scenarios merely because their IDs exist. |
| Scientific, engineering and harm review | Exact input review is preparation. Full candidate, outputs, claims and reproduction must receive the required panel and owner disposition. |
| Evidence ledger and lawful comparison | Existing descriptive records and held sources remain separate from inputs. Complete each evidence-family assessment and qualified external comparison or explicitly adjudicate applicability; do not claim synthetic self-comparison is empirical validation. |
| Reproducible report/package | Still pending: report, aggregate tables, input/code/environment hashes, seeds, output inventory, reproduction instructions and review response. |

## Implemented input preparation

`scripts/track003_reference_inputs.py` builds
`examples/demonstrators/track-003-reference-inputs.json`. Contract tests validate
the standard ledger, every assessment, closed parameter-to-assessment links,
exact regeneration and rejection of empirical/authority relabelling. The
fitness-for-use disposition is eligible for synthetic assurance only, not a
primary empirical estimate. No numeric uncertainty-inflation factor is invented
to make an incompatible source appear usable.

Fixed design values have unquantified uncertainty; beta shapes are invented
distribution controls, not participant counts or effective sample sizes.
Cost units are fictional currency/person-year, with an explicit one-year direct
healthcare perspective. No empirical price series or treatment benefit is used.
The closed synthetic cohort supplies one full case-year per expressed person,
with no entry, exit, death or competing event; all are assumed complication-free
at year start. Delay is the historical interval from first joint synthetic
diabetes/expressed-case membership to first detection, not clinical onset or a
genetic-testing interval and not necessarily contained in the reference year.

This artifact contains inputs and definitions only. No numerical results,
execution receipt, completed report, permission or completed-track claim is
created. The historical one-output receipt is unchanged and candidate-specific.

## Next implementation sequence

1. Integrate the candidate inputs into a bounded runner using the versioned
   random stream and existing mathematical contracts. Bind scenario-specific
   age/calendar/eligibility contexts rather than silently changing base context.
2. Implement all required scenarios, uncertainty summaries and subgroup-specific
   outcome/cost constructions with boundary, invariant and reproducibility tests.
   Shared-stratum scenarios must not invent a family sample size.
3. Complete evidence-family dispositions and a lawful comparison assessment.
4. Bind the complete inputs, definitions, code, seeds, expected output inventory,
   report specification and reproduction policy into one exact candidate.
5. Obtain required exact-candidate review/disposition before governed execution;
   then execute, independently rerun the implementation in a clean owner-operated
   environment, report and verify every original acceptance criterion.

Routine implementation, tests, scoped PRs and merges remain authorized. Keep
working on Track 003; do not advance to another track on preparation evidence.
