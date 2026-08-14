# Conductor closure plan — 2026-08-02

This plan sequences all remaining Tracks 002–017. It distinguishes work the
repository can complete autonomously from decisions that must be recorded by
an accountable external role. It is a planning artefact only: it does not
activate contracts, approve sources, or authorise a release.

## Recommendation

Use **Option A — gate-first with bounded parallel preparation**. Close the
source and landscape foundations (002 and 007) first, then review their
semantic and ledger consumers (008 and 009), then the deterministic engine and
demonstrators (010, 003, 005, 011 and 012). In parallel, keep synthetic tests,
review packets and receipt templates current for 013–017. This minimises
rework while preserving useful engineering progress without making unsupported
claims.

Option B (parallel implementation) is acceptable only for synthetic fixtures,
schema checks and documentation; it cannot close an evidence gate. Option C
(scope reset or archive) is a programme decision and should be used only after
a documented `revise` or `stop` disposition, never implicitly.

## Dependency sequence

```text
002 source authority ─┐
                      ├─> 008 semantic ─> 009 evidence ledger ─> 010 engine
007 landscape ────────┘                                      │
                                                            ├─> 003 clinical
                                                            ├─> 005 economic/social
                                                            ├─> 011 respiratory
                                                            └─> 012 paediatric
                                                                  │
                                                                  v
                                                     013 assurance/equity
                                                                  │
                                              014 release/API ─> 015 governance
                                                                  │
                                                     016 operations/security
                                                                  │
                                                     017 stable-v1 decision
```

Track 004 (federated node) may proceed with synthetic/offline exercises, but
controlled-node activation additionally depends on 002 rights, custodian
terms, independent operation, and release disclosure decisions.

## Closure matrix

| Track | Autonomous completion slice | Accountable gate still required | Contingency while pending |
|---|---|---|---|
| 002 | Exact source records, hashes, MIME/size, retrieval and fail-closed incidents | Scientific suitability; custodian licence/redistribution terms | Synthetic/public fixtures; no production adapter |
| 003 | Clinical profile schemas, negative tests and synthetic demonstrator | Clinical/scientific and patient/community disposition | Contract exercise only; no disease estimate |
| 004 | Trust-zone, signing, export and offline-run tests | Custodian authorisation; independent operator; disclosure owner | Offline synthetic node; no controlled data |
| 005 | Cost/economic schemas, scenarios and sensitivity fixtures | Health-economic/scientific and community acceptability review | Synthetic cost profile; no empirical cost claim |
| 006 | Archived internal review and reproducibility record | Any future scope change | Keep archived; reopen only by explicit change |
| 007 | Versioned protocol, search log, dedupe and exclusions | Public registration; independent methods; patient/community challenge | Dated local protocol; no completeness/novelty claim |
| 008 | Mapping states, ambiguity and version-diff tests | Source/clinical semantic review | Non-binding mapping; no contract freeze |
| 009 | Provenance, conflict, uncertainty and custody fixtures | Epidemiology, governance and engineering disposition | Synthetic ledger; no empirical activation |
| 010 | Deterministic estimands, seeded uncertainty and safety tests | Scientific/statistical, engineering and patient/community review | Synthetic alpha only; no burden estimate |
| 011 | Bronchiectasis profile and negative/compatibility tests | Respiratory clinical and community review | Synthetic profile only |
| 012 | Paediatric profile, age-boundary and cost fixtures | Paediatric, custodian, community and economic review | Synthetic child profile; no child-data use |
| 013 | Triangulation, equity and gap-report harness | Independent methods/equity/community disposition | Bounded gap report; no population equity claim |
| 014 | Aggregate API, provenance, SBOM and release-integrity checks | Data rights/custodian and release-authority decision | Offline package; no hosted release |
| 015 | Charters, remuneration, CARE/Indigenous and relationship templates | Constituted governance and partnership decisions | Governance draft only; no partnership claim |
| 016 | Threat model, backup/rollback and incident exercises | Independent security/operator review; named owner acceptance | Maintainer-only support; no service promise |
| 017 | Usability, reproduction, adoption and candidate checklists | Independent operator/user receipts; final release authority | Public synthetic candidate; keep v1 disabled |

## Receipt requirements

Every external receipt must name the role/organisation and independence or
conflicts; bind the decision to the exact commit, manifest or source digest;
identify protocol/evidence versions; state `pass`, `bounded`, `revise` or
`stop`; list conditions, dissent, residual-risk owner, scope and expiry/review
date. A subagent panel can prepare or challenge material, but cannot satisfy an
independent or accountable gate.

## Execution and contingencies

1. Maintain 002/007 packets and obtain exact-source and protocol decisions.
2. On acceptance, freeze 008/009 inputs and run their independent semantic and
   ledger review; on `bounded`, narrow supported scope and record conditions.
3. Run 010 and downstream synthetic demonstrators in dependency order. Any
   failed or conflicting decision produces `revise`/`stop`, not silent waiver.
4. Complete 013–016 evidence packets and tabletop exercises while gates are
   pending; keep runtime and release checks green.
5. Assemble the 017 candidate only after all required receipts are digest
   matched. Release authority chooses `pass`, `bounded`, `revise` or `stop`.

If a source route, reviewer, custodian, operator or owner is unavailable, the
safe fallback is to preserve the draft/fixture and narrow claims. No fallback
authorises controlled-data acquisition, redistribution, production support or
stable-v1 publication.

## Decisions needed from the programme owner

No decision is required to execute the repository-owned queue above. The only
future decisions are whether to accept a gate's recorded disposition and,
after all receipts are present, whether the release authority selects `pass`,
`bounded`, `revise` or `stop`.
