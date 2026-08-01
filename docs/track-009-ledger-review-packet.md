# Track 009 ledger review packet

**Status:** non-binding preparation; Track 009 remains blocked  
**Contract draft:** ledger contract v0.1.0  
**Activation rule:** do not freeze v0.4 schemas or migrations until Tracks 002
and 008 are formally complete.

## Decisions required

| Decision | Evidence | Accountable disposition |
|---|---|---|
| Parameter identity and estimand | Parameter schema, stable IDs, revisions and demonstrator profiles | approve, revise or reject |
| Evidence quality/transportability | Assessment schemas, rationales, bias and transfer limits | approve or revise |
| Conflicting evidence | Alternative groups, missingness and no-automatic-selection tests | approve, revise or bound |
| Rights and provenance | Source-release links, licence states, transformations and retention | approve, revise or reject |
| Revision/migration | Immutable history, impact tracing, migration design and supersession | approve or revise |
| Operational custody | Snapshot store, access control, signed checkpoints and recovery | approve, revise or reject |

## Repository evidence

- Parameter, evidence-assessment, assumption and analysis-specification schemas.
- Fail-closed source-release links, context compatibility, uncertainty and
  licence validation.
- Transactional append-only reference store with canonical hashes, chain
  verification, portable JSONL export and bounded queries.
- Synthetic demonstrator profiles for RBC-P002, RBC-P003 and RBC-P004; all
  remain `analysis_ready=false`.

## Required release packet before freeze

Provide a versioned ledger export, schema and migration identifiers, complete
source/semantic/transformation links, uncertainty and quality rationales,
conflict and missingness disposition, impact report, licence/retention state,
software/environment identity, and epidemiology, data-governance and
engineering decisions. Preserve superseded values; never silently select a
conflicting estimate or erase history.

## Safe continuation

Continue synthetic negative tests, migration fixtures and impact tracing. Do
not freeze v0.4 contracts, bind empirical demonstrators, or claim custodian
approval until upstream source/semantic gates and accountable review are closed.
