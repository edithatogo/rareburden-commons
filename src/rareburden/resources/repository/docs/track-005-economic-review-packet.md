# Track 005 economic/social burden review packet

**Status:** non-binding preparation; Track 005 remains blocked  
**Protocol draft:** RBC-P001D v0.1.0  
**Activation rule:** do not freeze cost contracts or collect patient/family data
until Tracks 009/010 and health-economics, ethics, governance and
patient/community gates are complete.

## Decisions required

| Decision | Evidence | Accountable disposition |
|---|---|---|
| Perspectives | Health-system, household and societal definitions | approve, revise or bound |
| Component taxonomy | Medical, social care, out-of-pocket, caregiver, productivity and education components | approve or revise |
| Valuation | Currency, price year, PPP, discounting and transfer-payment rules | approve, revise or reject |
| Overlap/missingness | Component boundaries, imputation and scenario rules | approve or revise |
| Distributional reporting | Subgroups, equity, who bears costs and who benefits | approve, revise or bound |
| Co-design and collection | Survey adaptation, translation, remuneration and acceptable burden | approve, revise or stop |

## Repository evidence

- Non-binding synthetic cost-ledger fixture with explicit perspective, price-year,
  valuation and missingness fields.
- Existing ledger/engine contracts preserve provenance, uncertainty and
  incompatible-unit failures.
- No patient/family data, empirical currency values or policy claims are
  present in the public fixture.

## Required closure packet

Provide a co-design record, component taxonomy, declared perspective, price and
currency conversion provenance, overlap/missingness assessment, scenario and
uncertainty outputs, distributional reporting plan, remuneration/translation
plan, ledger fingerprints, and health-economics, ethics, governance and
patient/community dispositions. Report observed, imputed, transferred and
scenario-based values separately.

## Safe continuation

Continue synthetic schema, overlap, unit, missingness and scenario tests. Do not
collect community data, assign universal monetary values, mix perspectives or
currencies silently, or publish economic estimates before review and resource
approval.
