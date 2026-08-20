# Programme risk register to v1.0

**Scale:** likelihood and impact are Low, Medium, High or Critical.  
**Rule:** a named role owns each risk before the associated track becomes active.

| ID | Risk | Likelihood | Impact | Leading indicator / trigger | Owner role | Primary response |
|---|---|---:|---:|---|---|---|
| R01 | Existing initiative already covers the proposed scope better | Medium | High | Landscape review identifies a near-complete equivalent | Programme lead | Partner, narrow or stop; publish adjacency decision |
| R02 | Rare-disease hierarchy causes systematic double counting | High | Critical | Parent/child sums exceed defensible envelopes or reviewers disagree materially | Semantic lead | Mutually exclusive burden hierarchy, overlap sensitivity, non-estimable states |
| R03 | Public data support only weak global extrapolation | High | High | Large share of parameters transferred from selected high-income cohorts | Epidemiology lead | Publish gap/transportability grades; bound claims; fund diverse nodes |
| R04 | Controlled-data access is delayed or refused | High | High | Applications exceed planned cycle or custodian cannot permit required output | Node lead | Public-data MVP, smaller parameter asks, local execution, alternate sources |
| R05 | Source terms prohibit reproducible redistribution | Medium | High | Licence review blocks raw or transformed release | Data stewardship lead | Release manifests, acquisition recipes and lawful derived aggregates only |
| R06 | Source interface or unversioned file changes silently | High | High | Checksum changes without release notice | Data engineering lead | Immutable cache, expected checksums, source-change failure and manual review |
| R07 | Rare-within-common fraction is misinterpreted as a causal DALY fraction | High | High | Policy users or analysts multiply common envelope without severity adjustment | Methods lead | Use precise terminology, separate case composition from burden composition, model cards |
| R08 | Small numbers or combined outputs create disclosure risk | Medium | Critical | Node output fails cell or differencing review | Privacy lead | Fail-closed disclosure engine, local approval, query budgets and suppression |
| R09 | Patient/community involvement is tokenistic | Medium | Critical | Decisions proceed without voting participation or remuneration | Community governance lead | Reserved decision rights, paid participation, documented dissent and appeal |
| R10 | Indigenous data are used outside locally determined authority | Medium | Critical | Proposed cross-country subgroup analysis lacks community governance | Indigenous governance lead | CARE-aligned local governance; do not extract generic categories without authority |
| R11 | Funding or founder dependence interrupts maintenance | High | High | No funded successor or host six months before RC | Governing Board chair | Co-leadership, institutional host, succession, maintenance reserve |
| R12 | Industry funding compromises perceived independence | Medium | High | Sponsor seeks method, prioritisation or publication control | Conflicts committee chair | Pooled funding, public agreements, no veto, conflict management |
| R13 | Software supply-chain compromise affects releases | Medium | Critical | Vulnerable dependency, compromised action or signing key | Security lead | Locked dependencies, pinned actions, SBOM, signing, rotation and incident drills |
| R14 | Statistical engine produces plausible but incorrect outputs | Medium | Critical | External reproduction or invariant test fails | Software assurance lead | Property/invariant tests, reference fixtures, independent implementation |
| R15 | Semantic or schema evolution breaks historical reproducibility | Medium | High | Old release cannot be loaded after update | Architecture lead | Immutable versions, migrations, compatibility tests and archived environments |
| R16 | Hosted atlas creates unsustainable operational burden | Medium | Medium | Reliability work displaces scientific work | Product lead | Normative static releases; hosted service remains optional and separately funded |
| R17 | Country comparisons stigmatise low-resource settings | Medium | High | Media or policy use converts data quality into performance ranking | Policy/community leads | No naïve league tables, uncertainty and ascertainment shown, co-designed narratives |
| R18 | Clinical/genomic definitions are not portable across ancestries or systems | High | High | Large discordance across node implementations | Clinical genomics lead | Local validation, ancestry-aware limitations, mapping variants, do not force pooling |
| R19 | Economic estimates embed inappropriate price or productivity assumptions | Medium | High | Results change materially under perspective or price assumptions | Health economics lead | Prespecified perspectives, local prices, distributional and sensitivity analyses |
| R20 | V1 scope expands faster than evidence and maintenance capacity | High | High | New outputs added without owner, tests or release criteria | Programme/product leads | Scope budget, track entry criteria, explicit Won't list, defer to post-v1 |
| R21 | Governance approvals become a late release bottleneck | Medium | High | Charters or decision bodies not operational by v0.5 | Programme lead | Start Track 015 early; governance gates embedded in each scientific track |
| R22 | A correction undermines confidence because prior versions are overwritten | Low | High | Pressure to replace files in place | Release lead | Immutable releases, supersession links, public correction log |
| R23 | Node environments cannot run the selected runtime or dependencies | High | High | Secure environment lacks supported Python/container capability | Federated engineering lead | Python 3.12 baseline, offline wheels/containers, language-neutral contracts, local variants |
| R24 | Public-source acquisition violates rate limits or click-through terms | Medium | High | Automated access is blocked or challenged | Data stewardship lead | No circumvention; manual registration and cached responses; custodian dialogue |
| R25 | Global burden framing obscures diagnostic journey and family outcomes | Medium | Medium | Outputs collapse to DALYs only | Community/economics leads | Parallel economic, social, diagnostic and gap products; do not force a single metric |

## Escalation

- Critical impact risks are reviewed at every milestone gate.
- A triggered privacy, legal, scientific-integrity or community-legitimacy risk can halt a track or release immediately.
- Risk acceptance states the affected release boundary, owner, compensating control and expiry date.
- Risks without an owner prevent the dependent track entering Active status.
