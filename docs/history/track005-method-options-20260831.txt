# Track 005 method options — 2026-08-31

Status: non-binding engineering proposal; owner selection is pending. This
document defines possible future tranches, not an implemented economic contract,
approved method, empirical activation, collection permission or release.

The [Track 005 specification](../conductor/tracks/005-economic-social-burden/spec.md)
and [review packet](track-005-economic-review-packet.md) retain the full economic,
scientific and participation requirements. Selecting a preparation route must not
silently remove those requirements or mark Track 005 complete.

## Existing evidence and decision boundary

The unchanged `examples/ledger/economic-social-synthetic.yml` contains an assumed
fixed value `1200.0`, unit `SYN` and minimum `0.0`. Its 2025 population period is
not a price year. A health-system label is not a typed perspective contract;
currency, PPP, discounting, transfers and payer boundaries remain unresolved.
Do not reinterpret this fixture, migrate its frozen export or use it as a rate
for any option below. New candidate fixtures would be separately named and bound.

These options are advisory alternatives. No option has been selected here.
Agent review does not establish independent review, community participation,
co-design, custodian authority or publisher permission.

Reporting context: the [CHEERS 2022 statement](https://pmc.ncbi.nlm.nih.gov/articles/PMC8793223/)
includes explicit perspective and currency/price-date reporting items. This is
background reporting guidance, not an endorsement of these proposed methods or
evidence that a cost-of-illness contract has been validated. The 2022 statement's
public bibliographic index was checked on 2026-08-31; no source dataset or full
article payload is retained by this tranche.

## Option A — Component-first, nonmonetary-first synthetic contract

**Recommendation:** implement a typed, validation-only component prototype before
implementing economic totals. This limits the next tranche to making assumptions,
incompatibilities and unresolved choices explicit.
Selecting A would authorize additive experimental schemas, a validation-only
interface, explicitly invented fixtures and regression tests. It would not
authorize a frozen taxonomy, a stable economic contract or integration into the
economic/count engines. Field definitions remain labelled experimental and
revisable; disputed semantics stay unassessed rather than silently resolved.
This is not a migration of the frozen Track 009 contract.

**Proposed scope and fields:** separately identify each invented component,
revision, component category, perspective label and definition reference, bearer
or payer role, recipient role, population, geography, observation period, quantity
kind, unit, denominator basis, evidence status and source/assumption references.
Represent missingness and overlap assessment explicitly, with rationale and
assessment status. Nonmonetary time, utilisation and participation measures remain
distinct quantities; recording time is not valuing time in money.
Distinguish the time provider from a payer and an intended recipient from an
observed beneficiary; an unknown benefit must not be inferred from either role.
Care/time can be present but unvalued, which is not zero burden.

**Proposed semantics:** distinguish an explicit zero from missing, not collected,
unassessed and not applicable. Require a value only for a value-bearing record. Preserve
component rows separately; do not sum across components or perspectives. Record
possible overlap without asserting that different identifiers establish mutual
exclusivity. Prospective perspective/category definitions need panel challenge
and owner disposition; their mention here does not freeze a taxonomy.
Payer/recipient labels do not determine an aggregate analytical perspective.

For a monetary-shaped record, retain unresolved currency, price-year and valuation
requirements as blockers, not defaults. Nonmonetary records require an explicit
reason when monetary fields are not applicable. No `SYN`-to-currency mapping,
time valuation, price conversion or economic calculation belongs in this tranche.
Structural validity must never turn such a record into an eligible cost input;
its economic-use status remains explicitly blocked or unassessed.

**Future acceptance tests:** valid invented component records round-trip without
altering their provenance; missing units, periods, denominator bases or status
rationales fail validation; missing values cannot become zero; inconsistent
value/status combinations fail; unsupported summation fails rather than silently
combining costs, time or perspectives. Tests distinguish unassessed overlap from
evidence of non-overlap and preserve all current ledger fixtures and exports.

**Trade-off:** makes later methods review and integration more inspectable, but
does not deliver a cost estimate or settle economic valuation. It introduces a
new contract surface requiring its own version and maintenance discipline.

**Contingency:** if component or perspective definitions remain disputed, retain
a candidate proposal and unresolved findings; do not publish them as a frozen
contract. Defer the disputed field semantics or select Option C. Do not turn an
unknown into an optional unchecked field merely to obtain passing tests.

## Option B — Bounded synthetic health-system cost calculation pilot

Selecting B would authorize preparation of a fully specified calculation and
fixture candidate, not immediate implementation or execution. That candidate
requires a further exact owner disposition because this packet selects no
valuation basis, fictional price year or unit-cost assumptions.

**Proposed scope and fields:** a separately specified, single-component invented
direct-health-system calculation. Require explicit perspective and boundary,
resource quantity, quantity unit and denominator, unit cost, fictional currency
identifier, declared price year, observation and valuation horizons, valuation
basis, assumption provenance and uncertainty/scenario status. Record who bears
the component and which costs are excluded before reporting a total.

**Proposed semantics:** an approved candidate could multiply compatible resource
quantity by an invented unit cost. It must first define whether quantities are
per-person or aggregate and establish compatible denominators and time bases.
Observation year cannot supply a missing price year. No real currency, rate,
discount factor or conversion series is selected by this proposal.

**Future acceptance tests:** a hand-checkable invented calculation reproduces;
unit, denominator, perspective, period and price-year mismatches fail before
calculation; missing parameters fail rather than defaulting to zero; every result
retains scenario-based status and explicit excluded components. Sensitivity cases
vary declared invented assumptions, not observations or inferred real-world rates.
The current `1200.0 SYN` fixture remains untouched and is not a calibration target.

**Exclusions:** household or societal totals, caregiver/productivity valuation,
transfer-payment allocation, cross-country comparisons, inflation/PPP conversion,
discounted multi-year estimates, patient-data collection and policy interpretation.
These are unsupported for the pilot, not permanently removed from Track 005.
The partial cost calculation supplies no efficacy or incremental-benefit claim.

**Trade-off:** yields a tangible calculation workflow sooner, but requires more
scientific decisions and can be mistaken for validated economic evidence. A
working calculation does not establish completeness or empirical fitness.

**Contingency:** prepare and review an exact calculation/fixture candidate before
implementation or execution. If perspective, valuation or denominator choices
remain unresolved, narrow to Option A or defer; do not select convenient rates
or reuse unrelated synthetic costs to clear the gate.

## Option C — Defer new economic contracts and calculations

**Scope:** retain existing fixtures and generic integrity checks; document open
economic questions without adding new schemas, component definitions or outputs.
The present unresolved fields and interpretation limits remain unchanged.

**Acceptance checks:** existing tests and frozen-artifact checks still pass;
documentation accurately reports missing economic capabilities and does not claim
Track 005 completion, actual participation or new authorization.

**Trade-off and contingency:** lowest design and interpretation risk, but no new
economic capability. Revisit when the owner can disposition a bounded proposal
with panel findings and, where applicable, real source or participation evidence.

## Recommendation, exclusions and stop conditions

Option A is recommended as the smallest useful design tranche. Approval of an
option would authorize only its recorded next scope; this options document itself
authorizes no implementation, execution or publication of economic results.
Keep methodology, exact-candidate review, data rights, actual co-design and release
decisions separate. No route supplies survey translation/remuneration evidence or
actual community consent. Stop on sensitive data, invented rights, inferred price
years, silent unit/perspective mixing, missingness treated as zero, unsupported
totals or claims that advisory simulation satisfies actual participation.
Neither A nor B includes source retrieval, survey collection or automatic
integration into Track 003. Component coverage must not be labelled total burden;
machine and human views must preserve the same missingness and scope limits.
