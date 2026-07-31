# Track 004 dependency review — Federated country-node execution package

**Review date:** 2026-07-27  
**Decision:** Blocked pending Tracks 009 and 010

## Historical findings — 2026-07-27 (superseded by reruns below)

- Track 006 was complete, while Tracks 009 and 010 were dependency-blocked.
- At that review point, the node contracts, disclosure policy, version negotiation and synthetic runner were not implemented in Track 004.
- Data-governance, patient/community, engineering and security gates remain required before any controlled-node pilot claim.

Repository-owned progress now includes an offline aggregate-export primitive
that rejects participant-level fields and suppresses small cells, with focused
negative tests. It does not connect to custodians or establish a pilot contract.

### Review rerun — 2026-07-29

Repository review result: **Pass with dependency and governance gates**. The
disclosure boundary and tests are deterministic, and the full validation gate
passes. Track 004 remains blocked pending Tracks 009/010 and data-governance,
patient/community, engineering and security review.

### Blocker resolution matrix — 2026-07-29

| Blocker | Local resolution | Remaining gate |
|---|---|---|
| Unspecified node/disclosure contracts | Added execution-manifest and disclosure-policy schemas plus synthetic fixtures | Data-governance and engineering approval |
| Participant-level export risk | Export validator rejects participant fields and suppresses small cells | Custodian-specific thresholds and privacy review |
| Controlled execution authorization | No custodian connection or person-level execution added | Approved node pilot and patient/community review |
| Signing/attestation | Manifest supports input/output fingerprints; signing remains unclaimed | Release/security authority |

The manifest builder now validates non-empty identifiers, bounds status values
and rejects incompatible major versions. It remains a deterministic offline
preflight helper; it does not attest an environment or authorize execution.

The preflight also captures only bounded runtime identity and a caller-supplied
lockfile fingerprint. It excludes credentials, host paths, and participant data;
environment attestation and controlled execution remain gated.

The synthetic `run_offline_node` helper now composes manifest creation with the
disclosure validator. It is deterministic and memory-only, with negative coverage
for participant-level rows; packaged execution is locally tested, but independent
second-operator installation and a controlled pilot remain open.

`build_synthetic_cohort` supplies aggregate-only multi-diagnosis and small-cell
fixtures. Manifest tests cover incompatible versions and failed/withdrawn terminal
states.

### Review rerun — 2026-07-31

Repository review result: **Pass for the bounded synthetic implementation**.
Correction records supersede rather than overwrite manifests; recursive log
redaction, participant-field rejection, small-cell suppression, deterministic
two-run execution, package checks, threat-model controls, operator guidance and
the non-binding pilot packet are present. The full repository gate passes.

This evidence does not constitute an independent custodian run, controlled pilot,
external review, signing/attestation approval, or approval to process controlled
data. Tracks 009 and 010 also remain dependency blockers.

ADR-0003 retains the controlled-environment pilot as a blocking v1 gate and
requires a bounded-scope reconsideration after Tracks 009 and 010 and before the
first v1 release candidate. Synthetic evidence cannot satisfy V1-FED-04.

### Remaining gate packet

| Gate | Exact evidence required |
|---|---|
| Data governance | Named authority approves lawful basis, custodian conditions, retention, withdrawal and disclosure thresholds |
| Patient/community | Recorded review of acceptable use, harms, equity, interpretation and framing |
| Engineering | Independent installation and synthetic execution from the operator guide on a supported environment |
| Security | Review of threat model, log redaction, dependency/supply-chain controls and signing/attestation design |
| Scientific | Approval of the analysis specification and interpretation for any proposed pilot |
| Pilot | Written custodian authorisation plus completed controlled-environment execution and export review |

### Automated review fixes — 2026-07-31

Security, packaging and lifecycle audits found fail-open aggregate fields,
weak credential redaction, permissive version/fingerprint contracts, absent
input/output schemas, caller-weakenable policy settings and overstated independent
execution. Repository-owned findings were remediated with aggregate allowlists,
nested-value rejection, monotonic supplied-policy comparisons, bounded
supplied-history guards, strict semantic versions, verifiable SHA-256 manifests,
correction invariants, hardened redaction, four schema-valid node fixtures,
installed-wheel node execution and corrected lifecycle evidence.

Signing/key custody, a genuinely independent operator, controlled execution and
the human review lanes remain open rather than being inferred from automation.
The bounded synthetic implementation now also includes an explicitly synthetic
common-analysis runner, immutable schema-aligned policy snapshots, stable
value-free query-shape fingerprints, immutable in-memory ledger snapshots and a
deterministic integrity-checked bundle for locally supplied wheels. These close
the repository-owned reference gaps without creating custodian authority.

Production approval of the common analysis contract, a complete pre-staged and
locked dependency wheel set, custodian-controlled durable policy/query storage
and clean second-operator installation remain open behind Tracks 009/010 and the
governance/security design gates.

## Disposition

Keep Track 004 **blocked**. Do not activate federated execution or controlled-environment pilot work until the evidence/parameter ledger and burden-engine dependencies are complete and the applicable external gates have documentary evidence.
