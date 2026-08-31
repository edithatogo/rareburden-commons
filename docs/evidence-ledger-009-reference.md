# Track 009 durable ledger reference

`rareburden.ledger_store.DurableLedgerStore` is a preparatory, local reference
implementation for validated parameter-ledger snapshots. It uses SQLite
transactions, sequential revisions, canonical JSON, content hashes, a
store-wide hash chain and database triggers that reject update and delete
operations.

The store:

- validates every snapshot with the current parameter-ledger schema and
  scientific invariants before insertion;
- serialises concurrent writers with `BEGIN IMMEDIATE`;
- rejects duplicate, skipped and non-positive ledger revisions;
- preserves every historical snapshot;
- verifies canonical content, receipt hashes and chain links;
- exports an ordered canonical JSON Lines history atomically; and
- fails closed on unsupported schema migrations.

JSONL export rejects a final destination that is a symlink, including a dangling
symlink, rather than replacing the link. An ordinary existing regular file may
be replaced atomically; choose a new destination when retaining an earlier
export. This final-path check does not establish parent-directory symlink
protection or resistance to filesystem check/replace races.

`ParameterLedger.query` provides bounded evidence-status, unit and source-release
filters. Returned records and portable documents are detached copies.
`require_compatible_context` prevents explicitly requested population or period
contexts from combining when values differ or required context is absent.
`conflict_groups` exposes alternative parameters that share the same quantity,
measure, metric, unit, population, period and semantic context; it never chooses
one automatically.

`validate_source_release_links` binds parameter references to supplied Track 002
release records and rejects missing releases or unusable licence states.
`render_markdown` produces a deterministic report that separates empirical or
modelled parameters from assumptions and exposes revisions, units, uncertainty,
licence, sources, rationales and limitations.

The parameter contract requires a positive revision, uncertainty status, licence
state, source-release and transformation links, semantic entity IDs, and strict
population/geography and period objects. Revision, date and age ordering
invariants fail closed. A separate non-binding assumption schema distinguishes
structural, distributional, transportability, missingness and operational
assumptions from empirical parameters.

This is not an authoritative custodian ledger. A process with database-owner
access can replace the file or remove its triggers. Production use therefore
still requires independently controlled storage, access controls, backup and
recovery, signed checkpoints, operational monitoring, migration approval and
data-governance authority.

The v0.1.0 ledger contract remains non-binding. These primitives do not select
between conflicting evidence, freeze schemas or replace epidemiology, methods,
data-governance or engineering review.

## Demonstrator readiness profiles

The non-binding profiles in `examples/demonstrators/` map the parameter roles
required by RBC-P002, RBC-P003 and RBC-P004 onto the ledger. A bound role must
resolve to a parameter with a compatible quantity type. An unbound role must
carry an explicit unresolved reason. `assess_demonstrator_readiness` separates
two conclusions:

- `contract_exercised` means at least one role has traversed the validated
  ledger contract;
- `analysis_ready` means every declared role is bound.

The repository profiles exercise all three contracts but intentionally remain
not analysis-ready. In particular, the paediatric profile does not treat a
synthetic run or generic population denominator as custodian approval or
controlled-data evidence.
