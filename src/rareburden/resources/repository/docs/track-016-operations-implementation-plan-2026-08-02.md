# Track 016 operations hardening implementation plan

**Status:** non-activating plan; production operations remain disabled.

## Blocker

Track 016 has repository-owned runbooks, bounded synthetic metrics and release
artefacts, but it does not yet have an executed clean-environment recovery or
rollback receipt, measured resource budgets, an approved retention/access
policy, or named primary and backup operational owners. These are prerequisites
for production-hardening activation and cannot be inferred from local tests or
from a subagent panel.

## Options

### Option A — staged clean-room exercises (recommended)

1. Freeze a synthetic release candidate and its manifest/checksums.
2. Build a disposable, locked environment from the source archive and wheel
   using only the documented offline inputs.
3. Measure install size, peak memory, CPU time, disk growth and representative
   workload duration against explicit budgets.
4. Exercise backup, restore, correction, withdrawal and rollback using a
   separate disposable environment; capture command transcripts, exit status,
   artifact hashes and redacted timestamps.
5. Re-run after a fault injection (corrupt artifact, interrupted restore or
   incompatible configuration) and verify fail-closed behavior.
6. Have the named primary/backup owners sign the support, retention and access
   dispositions before any production pathway is enabled.

This gives the strongest reproducible evidence while keeping all data
synthetic and avoids making service-level promises.

### Option B — hosted canary exercise

Run the same matrix in a short-lived hosted environment. This is faster for
platform-specific evidence, but introduces provider-specific retention,
credential and cost controls and therefore needs additional custodian/security
review. Use only as a contingency if clean-room tooling cannot reproduce the
target runtime.

### Option C — documentation-only deferral

Keep the runbooks and budgets as proposed, mark Track 016 blocked, and defer
activation. This is safe but does not close the release gate and should be used
only when no accountable owner or disposable environment is available.

## Recommendation and contingencies

Proceed with Option A. It is the least-privilege, lowest-cost path and matches
the repository's offline/reproducible boundary. If the source archive cannot be
rebuilt offline, use the retained wheel plus its provenance bundle and record
the limitation. If representative large-workload data are unavailable, use a
synthetic workload at the documented upper bound and leave real-world capacity
claims disabled. If an owner is not assigned, keep support and production
rollback disabled rather than substituting a panel decision.

## Dependency-ordered work packages

1. **Budget contract:** add a versioned machine-readable budget for package
   size, install disk, peak RSS, CPU time and workload duration; add negative
   tests for over-budget results.
2. **Policy contract:** add a retention/access policy covering logs, metrics,
   manifests, backups, rollback bundles and withdrawal records; default to
   metadata-only, least privilege and bounded retention.
3. **Exercise harness:** implement a clean-environment runner that records
   release identity, environment fingerprint, hashes, measurements, injected
   fault, outcome and redacted receipt.
4. **Recovery matrix:** execute backup/restore, correction/withdrawal and
   rollback scenarios, including one interrupted or corrupt-artifact case.
5. **Ownership packet:** record primary and backup owners, escalation path,
   recovery authority, support hours and handoff expiry without publishing
   personal credentials or unnecessary personal data.
6. **Panel review:** have repository subagents check completeness and runbook
   consistency. The panel may recommend dispositions but cannot provide the
   independent security/operator or release-authority acceptance required by
   Track 016.
7. **Activation decision:** keep the track blocked until the accountable
   security, operational-owner and release gates have evidence; otherwise
   publish only the bounded offline artefacts.

## Evidence required to close the blocker

- signed or otherwise attributable clean-environment exercise receipt;
- budget manifest and passing/negative test results;
- retention/access policy with scope, default, deletion and withdrawal rules;
- backup/restore/rollback fault-injection receipts with artifact hashes;
- named primary and backup owner acceptance and escalation route;
- independent security/operator review and release disposition.

No production deployment, external notification or publication is activated by
this plan.
