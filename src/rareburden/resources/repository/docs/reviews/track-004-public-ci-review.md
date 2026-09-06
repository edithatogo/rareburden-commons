# Track 004 hosted review repairs

Purpose: record review triage and the owner-authorised PR 317 repair, 2026-09-06.
Status: local remediation; hosted success and merge require separate observation.
Full local `make PYTHON=.venv/bin/python check` passed with 2,208 tests after
the repair. The focused policy, orchestration, survey, delivery and CLI suite
passed 262 tests; R agreement and the refreshed installed proof also passed.
The owner's reply "I approve" authorised the proposed repair, refreshed proof,
Actions rerun and subsequent merge. Statistical publication remains excluded.

## Actual statistic authorization

The hosted Codex P2 finding was valid: a survey ratio and Taylor SE were recorded
as a grouped count query. The optional `allowed_measures` policy field now
defaults to count only; it admits only `count` and
`survey_weighted_ratio_with_taylor_se`. The survey explicitly reserves the
latter with no grouping dimensions before computing. The supplied survey CLI
opts into both measures; existing count-only policies reject the survey before
reserving. Pure synthetic count runners cannot accept the survey measure.

This is an opt-in additive policy-schema extension. Older implementations reject
the new field rather than silently authorising it. Existing count-only canonical
policy bytes and hashes remain unchanged. Non-default measure permissions are
part of the immutable policy digest. Ledger restart verification retains the
actual measure and empty dimension tuple. Tests cover rejected permissions,
grouping mismatch, count-only rejection, explicit authorization and restart.

No old acceptance or proof manifest is rewritten. The original candidate remains
an exact historical snapshot; this corrective implementation and the updated
dependency capsule have separate evidence. This repair does not confer actual
custodian authority or approve public statistical output.

The 2026-09-01 frozen-candidate regression now reads exact historical copies of
the changed policy implementation, store and policy tests from `docs/history/`.
Their original manifest hashes are still enforced. Current behavior is tested
by the live policy/store/survey suites; updating code does not retrospectively
change the accepted historical candidate.

The current survey module (`49166cc2cd91e8c6bbe648c15c079a025fb2aba9c132a2b8b450bce592200e90`)
was rerun through the R reference script after explicit measure authorization
was added. Real ratio/SE, saved-rehearsal agreement and required-column decoder
agreement passed again. The estimator and data were unchanged; authorization
metadata and receipt hashes intentionally differ.

## Windows test scope

Eight integration cases incorrectly attempted POSIX directory fsync on Windows.
Only tests exercising actual POSIX durable delivery are marked POSIX-only.
Pure policy, survey, input-rejection, mocked-directory-sync and installation
preflight tests still run on Windows. Linux and macOS retain all integration
tests. No runtime fallback drops fsync or claims Windows durability.

## Amazon Q findings assessed

The automated comments were assessed against reachable code and the documented
owner-controlled-directory boundary, not accepted as eight critical defects.

- File-descriptor leak: not reproduced; the existing `finally` closes the
  descriptor if fsync raises. An injected-failure regression test proves this.
- Missing iterable validation: passing a non-iterable violates the typed API
  and raises before aggregation/reservation; the supplied runner provides a
  dataframe-derived list. This is not a demonstrated security or data-release bug.
- Missing second PSU: preflight requires both positive-weight PSUs per stratum
  before `_estimate`; malformed design tests fail before reservation.
- Path traversal: source suffixes and hashes are code constants. The operator
  intentionally selects a source root. Changing trusted code is not an
  untrusted-input traversal route in the supplied runner.
- Symlink TOCTOU: a malicious writer replacing files in the owner-controlled
  directory is outside the qualified boundary; no adversarial multi-writer
  security claim is made. Do not deploy in an untrusted writable directory.
- Missing recovery files: exceptions intentionally stop without recomputation
  or budget reset; the operator contract requires preserving and inspecting a
  partial stage. A missing-receipt test verifies no result is published.
- Integer overflow: Python integers do not wrap at 64 bits. Numeric preflight
  already rejects nonfinite/overflowing conversions; the huge-code test passes.
- Empty estimation input: positive-weight nonempty design is enforced by
  `_prepare`. Empty and all-zero-weight regressions explicitly verify no receipt.

These are agent advisory assessments, not independent human review. Any change
to the trust boundary or actual failing evidence reopens the affected finding.
