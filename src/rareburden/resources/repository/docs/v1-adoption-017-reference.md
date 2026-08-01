# Track 017 adoption and stable-release reference

This is a preparatory documentation and release-evidence scaffold. It does not
constitute a v1 release, support commitment or independent usability evidence.

## Role-based documentation map

| Role | Minimum guide | Evidence needed before v1 |
|---|---|---|
| Patient/community user | purpose, acceptable-use, uncertainty and harms | patient/community review |
| Analyst/researcher | quickstart, methods, ledger and reproducible workflow | independent reproduction |
| Developer | architecture, tests, extension and migration guidance | clean build and engineering review |
| Node operator/custodian | local execution, disclosure, rollback and incident procedures | node validation and governance approval |
| Data steward | source terms, provenance, retention, withdrawal and correction | data-governance approval |
| Release maintainer | manifests, checksums, SBOM, changelog and publication verification | release audit and named owners |

## Release evidence index

Every v1 claim must link to a versioned artefact, validation result, reviewer and
decision. Missing evidence remains a blocker; it is never inferred from a green
local test.

Required lanes: scientific, patient/community, data governance, engineering,
security, programme and release. Each lane records `pass`, `revise`, `bounded`
or `stop`, with residual risks and an owner.

## Reproduction checklist

1. Start from a clean clone and locked environment.
2. Verify source, package and provenance manifest hashes.
3. Run the documented offline validation command.
4. Compare reviewed outputs and record any expected nondeterminism.
5. Preserve the command transcript, environment identity and reviewer decision.

Two independent user runs, two clean release candidates, independent
reproduction and named primary/backup owners are required before v1.0.0.

## Accessibility preparation

The repository-owned presentation rules and bounded fallback are in
[`docs/accessibility-guidance.md`](accessibility-guidance.md). They provide
text alternatives, explicit missingness and non-colour-only requirements for
review; they do not replace the required accessibility review of rendered
Track 014/017 products.
