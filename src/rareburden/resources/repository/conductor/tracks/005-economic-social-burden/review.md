# Track 005 dependency review — Patient, family, economic and social burden module

**Review date:** 2026-07-27  
**Decision:** Blocked pending Tracks 009 and 010

## Findings

- Track 009 remains blocked and depends on Tracks 002 and 008.
- Track 010 remains blocked and depends on Track 009.
- No approved Track 005 economic/social component contract, perspective rules, parameter schemas, calculations or patient co-design have been completed; only a non-binding protocol draft exists.
- Health-economics, ethics, data-governance and patient/community review gates remain required.

## Disposition

Keep Track 005 **blocked**. Do not activate economic or social burden calculations until the evidence ledger and burden-engine contracts are complete and the required co-design and review gates are available.

### Repository-owned implementation slice — 2026-08-01

The non-binding Track 005 reference contract now records perspectives,
component separation, currency/price-year/PPP/discounting rules, transfer
handling, overlap and missingness states, subgroup reporting, and survey
safeguards. No economic calculation, participant collection, equity weighting,
or patient/community approval is claimed.

### External reviewer packet

- **Health economics:** approve perspectives, component taxonomy, valuation, price-year/PPP, discounting and overlap rules.
- **Ethics/patient-family:** assess acceptable burden framing, remuneration, translation, equity and co-design evidence.
- **Governance/engineering:** confirm lawful collection, parameter provenance, missingness and reproducibility controls.
- **Evidence required:** co-design record, ledger-linked synthetic examples, scenario outputs, review comments and dissent disposition.
