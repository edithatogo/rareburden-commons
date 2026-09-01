# Track 005 dependency review — Patient, family, economic and social burden module

## Selected component-first validation prototype — 2026-09-01

The repository owner selected Option A against exact proposal candidate
`1ed8ed425120f31f6d812230e924de6f3ca7b25f`. The implementation adds a separate
experimental schema, validation-only Python interface, explicitly invented
three-component fixture and regression tests. The frozen Track 009 schema,
economic ledger fixture, exports, manifests and all calculation engines are
unchanged.

Three actual role-separated agents reviewed engineering, security/data-use and
usability/community-harm boundaries. Findings on unsafe reference shapes,
pre-copy resource limits, missingness/coverage separation, component identity
and overlap-state consistency were corrected. All lanes passed the corrected
files without dissent. This was an owner-executed simulated-community challenge;
no actual community participation, representation, consultation, co-design,
endorsement, consent or independent review is claimed.

The contract preserves explicit zero separately from missing, not-collected,
unassessed and not-applicable states. Quantity missingness is distinct from
coverage, so an unpaid-care quantity remains visible while unvalued and its
coverage can remain unassessed. Bearer, payer, recipient, time provider and
beneficiary are separate required roles. Possible overlap requires a known
component reference; unassessed overlap is not evidence of exclusivity. The
whole document remains synthetic, experimental, unfrozen and blocked from
economic use. No total, valuation, price/currency conversion or engine API was
introduced.

Focused validation passed 28 tests. Root's full local `make check` passed 1,801
tests plus repository integrity and retained-provenance gates; the local test
timeout was 120 seconds and hosted defaults remain unchanged. Ruff, formatting,
typing, schema, safety and documentation checks passed.

Residual limitations: structural validation cannot establish taxonomy validity,
role truth, completeness, economic fitness, actual participation or absence of
sensitive text in allowed labels/rationales. Inputs must remain explicitly
invented; this validator is not a PII sanitiser. Asymmetric overlap metadata is
permitted and must remain unassessed rather than interpreted as scientific proof.

Disposition: accept this bounded experimental implementation while keeping Track
005 blocked. Stop on real or sensitive input, new source references, silent
defaults, error echo, aggregation/valuation paths, frozen-artifact drift or any
claim of total burden, economic fitness, participation, activation, completion
or release.

## Method-options preparation — 2026-08-31

`docs/track-005-method-options-2026-08-31.md` defines three proposed next scopes:
an additive component-first validation prototype (A), a separately specified
single-component invented cost pilot (B), or deferral (C). The recommendation is
A because it exposes quantity/context/missingness requirements without choosing
valuation or producing an aggregate. The trade-off is a new experimental
contract surface, not an economic result. Unresolved field definitions remain
candidate material for challenge, not frozen scientific defaults.

This is preparation under the owner's continuation direction. It does not
record an option selection, adopt a method, change the frozen ledger, activate
data or satisfy actual co-design. Track 005 remains blocked and its original
method/participation tasks remain pending. The exact option packet will retain
`owner_decision.status: pending`; a later scope-matched decision is required
before implementing the proposed contract or calculation.

Exact proposal candidate: `1ed8ed425120f31f6d812230e924de6f3ca7b25f`, tree
`cdf9d0fca1995d82bd649cc51ba06174bd9acb21`, retained at
`refs/tags/evidence/track005-method-options-2026-08-31`.
Manifest: `manifests/ledger/track005-method-options-20260831.json`, SHA-256
`3b72d6ece646ba56e96cc872ab3a43f502f2df679b75935f970e50af8b353127`.
The machine-readable packet is
`docs/decisions/2026-08-31-track-005-method-options.yml`.

The engineering/methods, security/data-use and usability/community-harm agents
each verified this binding and reported no blocking finding or dissent. This
is simulated role-separated advisory challenge, not independent review or
actual community participation. All three preserve owner selection as pending.
Root validation passed the full `make check` (1,761 tests) on the proposal
candidate, followed by three focused packet/preparation tests. Local pytest
used `--timeout=120`; the hosted timeout remains unchanged. Review finalized
on 2026-09-01; the proposal's 2026-08-31 identity is retained.

### Hosted review corrections — 2026-09-01

The CHEERS reporting-context paraphrase has explicit source/version, attribution,
CC-BY-4.0 notice, retrieval limitations and manual-paraphrase transformation in
`docs/track-005-method-options-provenance-2026-09-01.yml`. This supplements the
unchanged bound proposal; no full article payload or third-party rights are
inferred. The article's indexed licence notice was rechecked for the exact PMCID.

The declared evidence tag was pushed before PR creation. A separate fresh remote
clone resolved it to the candidate commit/tree above, matched both manifest file
hashes and passed `git fsck --full`. The remote annotated tag object is
`e67c9967bb1ce23486145a8206749fc3751a6cdd`; a review service's truncated snapshot
does not supply that remote ref. Consumers should fetch
`refs/tags/evidence/track005-method-options-2026-08-31` explicitly if absent.

## Bounded integrity review — 2026-08-31

Exact reviewed candidate: `8e1904d7b01638fc54918b68a2f69338c9e9bb36`,
tree `3667912a8e65bb6a61535d95f17c95712e9d08cf`.
Input manifest: `manifests/ledger/track005-integrity-inputs-20260831.json`,
original panel-reviewed SHA-256
`d11078abb3445faa8d1dc80688cfad5373b20a43555bcdec0c238e71a733896f`.
Panel assurance: simulated role-separated advisory panel. Engineering,
security/data-use and usability/harm agents each verified the candidate and
all six manifest file hashes and recommended bounded acceptance without dissent.
The documentation author also supplied the usability challenge; this is not
independent review. Owner-executed simulated-community challenge; no actual
community participation, representation, consultation, endorsement, consent or
independent review.

Root validation: `PYTEST_ADDOPTS='--timeout=120' uv run --no-sync make check`
passed, including 1,732 tests, frozen-ledger/containment, packaging, benchmark,
runtime projection and Conductor integrity gates. The timeout override is local
only; hosted defaults are unchanged. The original fixture and frozen export
hashes remain identical. The subsequent evidence commit adds this review binding
and manifest, not a different implementation or scientific artifact.

### Hosted evidence-retention correction

PR #280 review identified that squash history alone would not retain the exact
reviewed candidate. The repository's linear-history policy is unchanged.
Annotated non-release tag
`refs/tags/evidence/track005-contract-integrity-2026-08-31` now retains that commit.
The manifest adds only this retention reference; its amended SHA-256 is
`ce94f3ffda53666cfbd357cd93bba8ea5564b0f9e4ee4610c30f6412e0c4050c`.
Candidate identity, tree and all reviewed/frozen file hashes are unchanged.
All three advisory agents verified the amended binding and retained their
bounded pass; security separately confirmed the hosted P2 finding resolved.

The same retention protection was applied to earlier exact candidates:

- `evidence/track004-synthetic-assurance-2026-08-31` retains
  `9fd347ecbaf821fc0d73fe09c77760bf0484c3d5`.
- `evidence/track017-retained-guidance-2026-08-31` retains
  `1469a90951f7b920ffa98e09c2f7abe5869868bc`.

A fresh `git clone --no-checkout` from the public remote, without local object
sharing, resolved all three tags to their exact candidate commits and trees;
`git fsck --connectivity-only` passed. Normal clones retain these evidence tags.
Shallow or tag-excluding clones need the named tags fetched explicitly. They are
not version tags or releases and must not be removed as merged-branch cleanup.

Tracks 009/010 now have bounded completion evidence; their older blocked status
below is historical, not the current dependency disposition. Track 005 remains
**blocked** on its original methods and participation requirements.

This tranche corrects the review packet to the actual invented `SYN` fixture,
tests cost rejection by both count estimands before sampling and explicit context
failures, and rejects fixed values outside explicitly declared bounds at ledger
load. Equality, zero, permitted negative values and other distribution semantics
are preserved. No fixture, schema, valuation, conversion or economic calculation
is introduced or changed.

The engineering agent observed five failing regression cases before the fix and
36 passing new/existing ledger tests after it. The security agent's five economic
boundary tests passed and its separate cross-review found no blocking issue.
The documentation agent corrected unsupported machine-readable field claims and
passed the existing preparation contract. These are repository advisory roles,
not independent review, actual co-design, community endorsement or rights evidence.

Recommendation: deliver this structural safeguard under the existing bounded
implementation authority. Alternative: defer new economic-method work while
retaining the current fixture. Valuation, perspectives, overlap/missingness,
distributional reporting and actual participation remain unresolved; no dissent
was reported on the bounded repair. Stop if a later change introduces monetary
defaults, unsupported aggregation, sensitive data or manufactured participation.

## Owner-directed review routing — 2026-08-22

Clinical/scientific, patient/community and data-governance/custodian questions are routed to role-separated advisory agents. Their advice must be presented to the repository owner in an owner decision packet with options, trade-offs, contingencies, uncertainty, dissent and stop triggers. Security/engineering approval is routed to the owner as an owner-operated decision. None of these routes creates independent review, community consent, custodian authority or external scientific approval.

**Review date:** 2026-07-27  
**Decision:** Blocked pending Tracks 009 and 010

### Review rerun — 2026-08-01

Repository-owned preparation now includes a schema-valid, non-binding synthetic
health-system cost ledger fixture with explicit unresolved perspective,
currency, price-year, PPP, discounting, transfer and valuation limitations.
The full validation gate passes. This fixture is not an economic contract,
empirical estimate, patient/family co-design record or policy evidence; the
blocked disposition is unchanged.

## Findings

- Track 009 remains blocked and depends on Tracks 002 and 008.
- Track 010 remains blocked and depends on Track 009.
- No approved Track 005 economic/social component contract, perspective rules,
  valuation calculations or patient co-design have been completed. The new
  synthetic ledger fixture is preparation only and does not close those gates.
- Health-economics, ethics, data-governance and patient/community review gates remain required.

## Disposition

Keep Track 005 **blocked**. Do not activate economic or social burden calculations until the evidence ledger and burden-engine contracts are complete and the required co-design and review gates are available.

### External reviewer packet

- **Health economics:** approve perspectives, component taxonomy, valuation, price-year/PPP, discounting and overlap rules.
- **Ethics/patient-family:** assess acceptable burden framing, remuneration, translation, equity and co-design evidence.
- **Governance/engineering:** confirm lawful collection, parameter provenance, missingness and reproducibility controls.
- **Evidence required:** co-design record, ledger-linked synthetic examples, scenario outputs, review comments and dissent disposition.

### Preparation refresh — 2026-08-01

`docs/track-005-economic-review-packet.md` records the decisions and evidence
needed before activation. It is repository-owned preparation and does not
constitute co-design, ethics approval, economic review or patient/community
approval.
