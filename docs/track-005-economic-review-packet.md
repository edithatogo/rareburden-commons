# Track 005 economic/social burden review packet

**Status:** non-binding preparation; Track 005 remains blocked  
**Protocol draft:** RBC-P001D v0.1.0  
**Activation rule:** do not freeze cost contracts or collect patient/family data
before the applicable health-economics, ethics, governance and patient/community
gates are dispositioned. Tracks 009/010 have bounded completion evidence; that
does not activate this economic contract or supply missing valuation rules.
Repository review uses advisory agents and owner disposition. Actual data rights,
co-design, participation and collection permissions remain evidence-bound facts.

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

- The non-binding fixture `examples/ledger/economic-social-synthetic.yml` contains
  one assumed `cost_per_person` parameter with unit `SYN`, fixed value `1200.0`,
  minimum `0.0` and `uncertainty_status: not_quantified`. Its population period
  covers 2025; that is not a declared price year.
- A health-system perspective appears in the label and assumption rationale,
  not as a separately validated perspective field. Currency, price year, PPP,
  discounting, transfers and payer boundaries are explicitly unresolved in prose.
  The fixture does not supply dedicated valuation or missingness contract fields.
  Its generic ledger validity is not evidence that those economic contracts
  exist or that cross-component aggregation is safe.
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

Advisory health-economics, ethics and community/harm challenge can identify
problems and recommend options; the owner records the repository disposition.
Owner-executed simulated-community challenge; no actual community participation,
representation, consultation, endorsement, consent or independent review.
An agent assessment is not a co-design record, and neither agents nor the owner
can manufacture third-party rights or participation. Survey co-design and
remuneration evidence remain required before claiming those activities occurred.

## Remaining decisions and bounded recommendation

The perspective, taxonomy, valuation, overlap/missingness and distributional
decisions above remain unresolved. So do survey adaptation, translation,
remuneration, acceptable-use safeguards and the evidence needed for collection.
This packet introduces no new perspective definitions, conversion method or
monetary interpretation of `SYN`.

The recommended option is to retain the invented fixture and strengthen generic
contract failure tests without changing its scientific meaning. This improves
integrity but cannot complete the economic module. Alternatively, defer economic
contract activation until the owner disposes of a separately prepared methods
proposal with agent challenge and applicable real-world evidence. Uncertainty
about valuation, who bears costs and stakeholder needs remains unresolved.
Stop on unsupported valuation, missing rights, sensitive data, silent perspective
mixing or claims that simulated review establishes actual co-design.

## Safe continuation

Continue synthetic schema, overlap, unit, missingness and scenario tests. Do not
collect community data, assign universal monetary values, mix perspectives or
currencies silently, or publish economic estimates before review and resource
approval.
