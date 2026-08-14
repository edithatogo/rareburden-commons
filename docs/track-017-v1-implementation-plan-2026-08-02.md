# Track 017 stable-release implementation plan

**Status:** non-activating plan; no v1 tag or support promise is authorised.

## Blocker

The repository has role-based documentation and synthetic reference tests, but
there is no independent usability/reproduction receipt, accepted ownership and
sustainability model, or stable-release evidence package. Local tests and a
subagent panel can prepare and check evidence; they cannot be represented as
independent user/operator activity or release authority.

## Options

### Option A — staged offline release-candidate programme (recommended)

1. Freeze a candidate commit and create two clean builds from locked
   environments (source archive and wheel paths).
2. Give the same public quickstart and reference workflow to two independent
   operators without maintainer intervention; capture task completion, defects,
   environment, timings and redacted receipts.
3. Run one independent reproduction against the candidate and compare reviewed
   outputs using hashes and an explicit equivalence tolerance.
4. Assemble a v1 evidence index mapping every acceptance criterion to a receipt,
   limitation or bounded exclusion.
5. Record primary/backup owners, succession, support scope, cost assumptions
   and expiry/renewal conditions.
6. Submit the packet to the accountable multi-lane gates, then tag v1 only if
   the release authority records release.

This is the strongest path because it is reproducible, low-cost and preserves
the project's offline and aggregate-only boundaries.

### Option B — hosted cross-platform canary

Run candidate builds and usability sessions in disposable hosted Linux/macOS/
Windows environments. This can expose platform drift sooner, but adds provider
retention, credentials, cost and data-governance obligations. Use only if
Option A cannot cover the supported matrix.

### Option C — bounded pre-v1 release

Publish a versioned release candidate with an explicit “not stable / no support
promise” scope statement. This improves discoverability but does not satisfy
the stable-v1 acceptance criteria and must not be labelled v1.0.0.

## Recommendation and contingencies

Proceed with Option A. If two independent users cannot be recruited, retain the
candidate as pre-v1 and record the exact missing receipt. If an equivalent
reproduction cannot be achieved, narrow the supported workflow and publish the
discrepancy rather than relaxing equivalence. If ownership or cost acceptance
is absent, keep support and stable-release claims disabled. If a platform cannot
be reproduced cleanly, remove that platform from the supported matrix until
new evidence exists.

## Dependency-ordered work packages

1. **Candidate freeze:** record commit, lockfile, source/wheel hashes, supported
   environment and reproducible build commands.
2. **Usability packet:** provide a fixed task script, success criteria,
   accessibility prompts, defect taxonomy and redacted receipt template.
3. **Independent reproduction:** compare outputs, provenance, limitations and
   hashes; preserve non-equivalence as a finding.
4. **Ownership and sustainability:** record primary/backup maintainer,
   incident, reviewer and succession roles, support boundaries, costs and
   institutional or bounded interim host.
5. **Evidence index:** link every v1 criterion to exact artefacts and mark
   unsupported capabilities as exclusions.
6. **Panel review:** use repository subagents to check completeness, traceability
   and consistency; retain external/accountable decisions as separate gates.
7. **Release decision:** release, bounded exclusion, revise or stop; only the
   release-authority record can permit v1.0.0 tagging.
8. **Public verification:** after approval, publish artefacts and verify them
   from the public instructions; otherwise leave publication disabled.

## Evidence required to close the blocker

- two independent usability receipts;
- two clean candidate build receipts;
- one independent reproduction and equivalence report;
- maintainer/reviewer/incident/succession roster with backups;
- approved cost and support model or bounded interim ownership;
- complete v1 evidence index and accountable multi-lane release disposition;
- public artefact verification receipt after approval.

No user recruitment, external communication, stable tagging or publication is
initiated by this plan.
