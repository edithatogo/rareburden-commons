# Track 017 adoption and stable-release reference

This is a preparatory documentation and release-evidence scaffold. It does not
constitute a v1 release, support commitment or independent usability evidence.
This single-developer repository uses role-separated advisory agent panels and
an attributable repository-owner disposition; no additional person is required
or represented as an independent authority.

## Role-based documentation map

| Role | Minimum guide | Evidence needed before v1 |
|---|---|---|
| Patient/community perspective | purpose, acceptable-use, uncertainty and harms | community/harm agent challenge; owner disposition |
| Analyst/researcher | quickstart, methods, ledger and reproducible workflow | owner-operated reproduction; non-independent |
| Developer | architecture, tests, extension and migration guidance | automated checks and engineering agent challenge |
| Node operator/custodian | local execution, disclosure, rollback and incident procedures | owner-operated node evidence; actual custodian policy remains external |
| Data steward | source terms, provenance, retention, withdrawal and correction | rights/governance agent challenge; publisher terms remain facts |
| Release maintainer | manifests, checksums, SBOM, changelog and publication verification | release agent challenge and owner disposition |

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

Two role-separated agent assessments, two clean release candidates and an
owner-operated reproduction are repository evidence before v1.0.0. They do not
become independent approval. Backup-owner continuity is an explicit limitation
when no backup is attributable.
