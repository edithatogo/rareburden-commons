# External review request template — stable v1 candidate

**Status:** draft request; not sent and not evidence of consent.  
**Candidate:** record the exact commit, manifest ID and artefact digest before
sharing.

## Submission and return workflow

1. The maintainer freezes the candidate identity and creates one copy of the
   receipt template per gate; no gate is requested against a moving branch.
2. The accountable body records its remit, authority or independence basis,
   conflicts/quorum, evidence reviewed, decision, conditions, dissent and
   expiry in the receipt. Restricted material may be referenced by a durable
   pointer without being copied into the repository.
3. The submitter returns the receipt through the agreed secure channel. The
   maintainer records only the receipt ID, digest match, status and locator in
   the register; a missing or incomplete return remains `pending`.
4. A candidate change, expired decision, unresolved discrepancy or changed
   scope requires a new receipt or explicit supersession. Never edit a signed
   receipt in place.

This document is a draft routing aid and has not been sent. It does not name
recipients, create an appointment, or constitute a review panel.

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
