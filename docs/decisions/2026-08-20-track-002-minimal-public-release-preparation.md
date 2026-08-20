# Track 002 minimal public-release preparation — 2026-08-20

**Decision maker:** repository owner

**Authority exercised:** repository-controlled preparation only

**Publication status:** not authorized

## Decision

Prepare an exact, hash-identified public candidate containing only the July
2026 Orphadata epidemiology and alignment XML files and the three canonical
MONDO `v2026-08-04` artifacts recorded in
`track-002-minimal-public-release-scope-2026-08-20.yml`.

WPP remains private under the current owner disposition. WHO GHE remains a
private candidate or metadata-only. HPO remains limited to individually
cleared assets and is not included in this candidate. PanelApp and every
controlled or credentialed source remain excluded. No further private capture
is authorized until the capacity and source-specific credential gates pass.

## Reconciliation with the existing public projection

The earlier public-projection audit recorded that WPP, ClinVar and a bounded
World Bank probe already existed in the public Hugging Face dataset. This
decision supersedes that audit as release-scope authority but does not erase
the historical observation.

The WPP object cannot truthfully be described as private while that public
object remains observable. Removing it or changing hosted visibility is an
external mutation and requires a separate exact authorization, followed by
remote verification. This preparation therefore records the discrepancy as a
pending remediation gate and performs no hosted deletion or visibility change.

## Claims boundary

The candidate may support only bounded source-snapshot, provenance and
engineering statements. It must not imply comprehensive or systematic
coverage, global representativeness, confirmed novelty, independent review,
community authority, clinical validation, partnership, access or external
approval.

## Gates retained

- exact five-artifact candidate packaging and digest verification;
- dated live terms/source-change exercises for Orphadata and MONDO;
- candidate-bound rights, attribution and third-party exclusion audit;
- Track 007 disposition compatible with bounded claims;
- separate handling of the already-public WPP object;
- a final owner publication decision bound to the exact commit and artifacts.

This decision neither publishes a release nor closes Track 002 or Issue #2.
