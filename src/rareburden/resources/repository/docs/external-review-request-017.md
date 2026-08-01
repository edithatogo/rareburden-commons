# External review request template — stable v1 candidate

**Status:** draft request; not sent and not evidence of consent.  
**Candidate:** record the exact commit, manifest ID and artefact digest before
sharing.

## Requested response

Before recording a decision, complete the identity and scope fields:

- candidate commit SHA, manifest ID and artefact digest;
- reviewer name, accountable role and organisation (if applicable);
- independence statement, conflicts of interest and any dissenting member;
- evidence and protocol versions reviewed;
- decision date, conditions, residual-risk owner and expiry/review date.

Please select one disposition for the requested gate:

- `pass` — the supplied scope is acceptable for the stated use;
- `revise` — changes are required before reconsideration;
- `bounded` — only the listed reduced scope is acceptable;
- `stop` — do not proceed with the proposed release or use.

An owner or release-authority decision must be labelled separately from an
independent scientific, patient/community, custodian or operator receipt. A
technical subagent or automated test may be cited as preparation evidence, but
cannot be identified as the accountable decision-maker.

## Gate-specific questions

### Scientific methods

Are the estimands, disease definitions, overlap rules, uncertainty,
transportability, sensitivity analysis and permitted language adequate for the
candidate scope? Identify any unsupported comparative, causal or global claim.

### Patient/community

Are the proposed uses, framing, harms, equity limitations and correction/
complaints pathways acceptable? Identify wording or outputs that require
removal, reframing or further participation.

### Data governance/custodian

Are source terms, redistribution, retention, withdrawal, disclosure thresholds,
Indigenous/CARE obligations and controlled-data boundaries acceptable? State
any conditions for future node execution.

### Security/operations

Are the threat model, supply-chain controls, attestation, logging, backup,
rollback and incident procedures adequate for the stated support scope? State
required owners and exercises.

### Programme/sustainability

Are the primary/backup owners, support promise, costs, succession, deprecation
and institutional-host arrangements acceptable? Distinguish confirmed
relationships from proposals.

### Release authority

Does the evidence packet justify publication of the exact candidate scope? If
not, specify the bounded exclusions or required remediation. This request does
not ask for a `v1.0.0` tag unless every blocking criterion has evidence.

## Standing exclusions

Until the relevant decisions are recorded, the candidate excludes controlled
data, custodian deployment, global representativeness, unsupported country
comparisons, patient-facing policy conclusions, institutional support promises
and stable-v1 publication.
