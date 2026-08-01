# Track 011 dependency review — Bronchiectasis rare-aetiology demonstrator

**Review date:** 2026-07-27  
**Decision:** Blocked pending Tracks 008, 009 and 010

## Findings

- Tracks 008, 009 and 010 are blocked and have not provided the semantic, evidence-ledger or burden-engine contracts required by this demonstrator.
- No approved Track 011 protocol, aetiology scope, overlap model, transportability model or analysis has been completed; only a non-binding protocol draft exists.
- Respiratory clinical, patient/community and engineering review gates remain required.

Repository-owned preparatory work now includes a schema-valid synthetic analysis
specification and limitations report. These artifacts exercise the contract only;
they do not assert bronchiectasis aetiology, activate the protocol or replace
reviewed ledger/semantic inputs.

### Review rerun — 2026-07-29

Repository review result: **Pass with dependency and clinical gates**. The
synthetic artifacts are bounded and reproducible, and the full validation gate
passes. Track 011 remains blocked pending Tracks 008–010 and respiratory,
methods, patient/community and engineering review.

## Disposition

Keep Track 011 **blocked**. Do not activate bronchiectasis analysis or freeze multi-aetiology contracts until the prerequisite tracks are complete.

### Repository-owned implementation slice — 2026-08-01

The plan now records the existing non-binding RBC-P003 draft, preparatory
aetiology category set, and explicit multi-aetiology/unclassified boundary as
repository contracts. The synthetic fixture remains assurance-only; no pinned
clinical ontology, empirical fraction, respiratory review or activation is
claimed.

### External reviewer packet

- **Respiratory clinical:** approve denominator, aetiology categories, overlap and diagnostic-capacity framing.
- **Methods:** inspect referral/transportability, unclassified causes, uncertainty and independent comparison.
- **Patient/community:** assess language, harms, equity and acceptable interpretation.
- **Evidence required:** RBC-P003 decision record, synthetic analysis, setting scenarios, validation report and dissent disposition.
