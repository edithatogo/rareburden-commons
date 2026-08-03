# Panel assurance report — frozen candidate

**Status:** `panel_assurance`; recommendation only, not an external receipt or
release approval. **Candidate tag:** `candidate-2026-08-03` (peeled commit
`9e668ce9dc860daeb45dac135b58ba203d30b239`). **Manifest:**
`rel-b213c531a6b754940f80ab70`. **Input digest:**
`d3aafd7367609050d6a4c9926a8ddca3013085362f78abd319dd582135612389`.

Three role groups reviewed the candidate against the panel-agent task contract:
methods/source and custodian governance; patient/community and release
integrity; independent operator and operational ownership.

## Consolidated recommendations

| Gate | Panel recommendation | Permitted now | Prohibited claim |
| --- | --- | --- | --- |
| Scientific/source methods | `bound` | Methods-only and synthetic/public preparation; narrow Orphadata + UN WPP candidate posture | Validated prevalence/incidence, completeness, causal or broad cross-source claims |
| Custodian/data governance | `bound` | Metadata, URLs/releases/hashes and derived-aggregate design; no raw redistribution | Confirmed redistribution, archival, retention or third-party rights |
| Patient/community | `bound` with revise trigger | Offline docs, synthetic fixtures, public methods and accessibility planning | Consent, endorsement, patient-facing deployment or Indigenous/LMIC conclusions |
| Independent operator | `revise`/pending | Repository-owned clean-room rehearsal and synthetic recovery exercise | Independent reproduction or independent-release claim |
| Operational owners | `revise`/pending | Ownership packet and bounded maintenance preparation | Named-owner acceptance, production support or capacity promise |
| Release authority | `bounded` recommendation only | Synthetic/public preparation snapshot | Stable-v1 tag, hosted API, controlled activation or release authorization |

## Evidence and uncertainty

- Exact candidate pins and hashes establish identity, not source meaning, rights
  or fitness.
- Orphadata and UN WPP are the narrowest plausible preparation path; exact
  product semantics, geography/year extraction, denominators, coverage,
  update cadence, bias and uncertainty remain unresolved.
- WHO GHE and World Bank material remain candidate-only; licence, third-party
  material, retention and redistribution conditions are not fully confirmed.
- Synthetic operations, budget, rollback and package checks are repository
  evidence, not independent operator evidence.
- No constituted patient/community body, custodian, independent operator,
  named owner or release authority supplied a receipt.

## Options for remaining blockers

### Option A — Recommended: bounded panel-only continuation

Keep the candidate and register fail-closed; run clean-room and synthetic
recovery rehearsals, remove wording implying endorsement or production use, and
retain Orphadata/WPP as conditional preparation only. This yields the strongest
safe result without inventing authority.

### Option B — Narrow further

Use metadata/hash-only and synthetic fixtures, deferring all source-derived
outputs until terms and semantics are confirmed. This reduces rights and
interpretation risk but reduces utility.

### Option C — Stop or supersede

Stop the affected claim or supersede the candidate if unresolved terms,
accessibility/harm concerns, reproduction failure or ownership gaps cannot be
bounded. Preserve the discrepancy and immutable history.

**Recommendation:** Option A, with Option B for any source or claim whose terms
or semantics remain unresolved, and Option C on a material safety, rights or
reproduction failure.

## Required follow-up

1. Keep all six qualifying register entries `pending`.
2. Execute the clean-room operator rehearsal and synthetic rollback exercise.
3. Complete the panel wording/accessibility pass and remove endorsement or
   production implications.
4. Maintain source-to-metric/denominator and licence/redistribution evidence
   as explicit unresolved fields.
5. Reopen the register only if an attributable, digest-bound receipt becomes
   available; reject receipts bound to any commit other than the peeled tag
   commit above.

## Offline clean-node rehearsal status — 2026-08-03

The repository-owned rehearsal was attempted with the normative Python 3.13
runtime and failed before installation: the local macOS arm64 wheelhouse
contains a hash-pinned PyYAML 6.0.3 `cp314` wheel but no compatible `cp313`
wheel. This is an environment/wheelhouse availability failure, not evidence of
package incompatibility. A supplemental `PYTHON_VERSION=3.14` run completed
with network disabled and produced `dist/offline-install-receipt.json`.

The 3.14 receipt is useful local compatibility evidence only; it does not
replace the Python 3.13 release-candidate rehearsal or an independent operator
receipt. The release matrix therefore remains unchanged and the clean-node
follow-up remains open.

### Contingencies

1. **Recommended:** obtain a matching `cp313` PyYAML wheel in the pinned
   wheelhouse (or run the existing 3.13 job on the supported hosted Linux/macOS
   runner), then rerun `make offline-node-ci PYTHON_VERSION=3.13`.
2. Retain the successful 3.14 run as supplemental evidence while the 3.13
   wheelhouse is repaired; do not relabel it as release or independent evidence.
3. Do not move the normative release runtime to 3.14 without a separate
   compatibility decision, workflow update and refreshed candidate manifest.
