# Track 002 qualifying-evidence sourcing plan

**Scope:** approved bounded Option A (Orphadata + UN WPP preparation; WHO
candidate-only; World Bank probe-only).

## Evidence sequence

1. **Prepare the source packet.** For each exact Orphadata and UN WPP record,
   bind URL, release, retrieval time, MIME/size, SHA-256, scope, metric/unit,
   attribution, terms snapshot, retention and redistribution posture.
2. **Run the panel preflight.** Subagent panels check completeness, metric and
   denominator compatibility, bias/limitations, rights conditions, and all
   negative/fail-closed paths. Record dissent and unresolved questions.
3. **Source the scientific disposition.** Obtain a qualifying methods decision
   against the exact packet: estimand, denominator, geography/year, units,
   coverage, bias, transportability, update cadence, intended use, limitations,
   and approve/bound/revise/reject outcome.
4. **Source the custodian/data-governance disposition.** Obtain a qualifying
   terms decision against the same digest: lawful purpose, raw-byte retention,
   derived-output rights, redistribution, third-party material, attribution,
   withdrawal/correction, expiry, and named authority.
5. **Source Track 007 evidence.** Preserve the registered protocol identifier,
   dated rerun logs, raw-export hashes, deduplication/exclusion counts,
   independent methods challenge, and patient/community interpretation. Until
   then, keep landscape claims provisional.
6. **Source operator evidence.** Have an operator outside the implementation
   role run the clean checkout/manifest workflow, compare hashes, record
   environment and discrepancies, and return a signed or durably located
   receipt.
7. **Reconcile and decide.** Bind all receipts to the candidate manifest and
   commit. Narrow or remove any source/claim with conflicting conditions. Only
   then request a bounded/revise/stop v0.3.0 release decision.

## Options

- **A (recommended):** qualify Orphadata and UN WPP independently, retain WHO
  and World Bank as deferred candidates, and release only the bounded scope.
- **B:** use a methods/manifest-only or synthetic-only preview while receipts
  are pending; no empirical or novelty claims.
- **C:** remove all live-source use from v0.3.0 and defer acquisition entirely.

## Contingencies

- No qualifying scientific authority: retain panel recommendation, narrow to
  descriptive/synthetic output, and do not activate.
- Terms unclear or third-party material unresolved: metadata/hash-only or
  operator-local retrieval; no raw cache or redistribution.
- Track 007 registration/challenge unavailable: use B and remove novelty,
  completeness, partnership and endorsement claims.
- Operator receipt unavailable: retain registration-only mode; no independent
  reproduction claim.
- Conflicting receipts: preserve dissent, suspend affected source/claim, and
  require a new digest-bound disposition.

## Receipt minimum

Use `docs/external-gate-receipt-template.yml`. Each receipt must include a
unique ID, accountable role and authority basis, conflicts/quorum or
independence basis, commit/tag and manifest digest, evidence references,
decision, conditions, dissent, expiry/review date, and supersession pointer.

Subagent panels can prepare and challenge these packets but cannot satisfy the
qualifying authority or independent-operation requirement.

The executable request register is
`docs/track-002-qualifying-evidence-request.yml`; all requests intentionally
remain `pending` until qualifying receipts are returned.
