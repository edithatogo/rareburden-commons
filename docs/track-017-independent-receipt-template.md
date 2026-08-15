# Track 017 usability and owner-reproduction receipt template

**Status:** template only; legacy filename retained for compatibility.

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
  operator_role: "advisory-usability-agent | repository-owner-operator"
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
- agent usability and owner-operated reproduction are bounded repository
  evidence and must not be described as independent, human, community,
  custodian, external or stable-release approval.
