# Track 017 independent usability and reproduction receipt template

**Status:** template only; completion requires an independent operator or user.

Copy this template once per run. Do not include credentials, participant data,
raw private logs or uncontrolled source material.

```yaml
receipt_schema: "0.1.0"
receipt_kind: usability | reproduction | clean_build
candidate:
  commit: "<40-character commit>"
  release_manifest_id: "<manifest id>"
  artefact_sha256: "<sha256>"
environment:
  os: "<name/version>"
  runtime: "<runtime/version>"
  isolation: "clean-clone | disposable-environment"
run:
  started_at_utc: "<timestamp>"
  commands: ["<public command>"]
  task_ids: ["<task identifier>"]
  outputs_sha256: ["<sha256>"]
  outcome: "pass | qualified | fail"
  discrepancies: []
  intervention: "none | documented"
review:
  operator_role: "independent-user | independent-operator"
  reviewer_role: "<role or panel reference>"
  decision_expiry_utc: "<timestamp>"
  notes: "<bounded findings and limitations>"
```

Acceptance rules:

- `pass` requires all task IDs and expected outputs to be completed without
  maintainer intervention;
- `qualified` or `fail` must preserve the discrepancy and block the affected
  stable-release claim until dispositioned;
- equivalence is assessed against reviewed output hashes and documented
  tolerances, never by visual similarity alone;
- a repository test, CI result or subagent panel is not an independent receipt.
