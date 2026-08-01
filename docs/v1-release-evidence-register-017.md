# Stable v1 release evidence register

**Track:** 017-documentation-adoption-v1  
**Status:** preparatory register; no release gate is passed by this document  
**Revision:** 2026-08-01

This register indexes the blocking criteria in `docs/v1-acceptance-criteria.md`.
A row is `pass` only when the linked artefact, validation result, reviewer
decision and residual-risk owner are present. Local green checks do not
substitute for external, independent or governance evidence.

| Lane | Required evidence | Current state | Contingency if unavailable |
|---|---|---|---|
| Scientific | Demonstrator triangulation, uncertainty/sensitivity outputs and independent review | `blocked` pending Track 013 | Remove unsupported comparative/global claims |
| Patient/community | Harms, interpretation, acceptable use, equity and framing review | `blocked` | Exclude patient-facing and policy claims |
| Data governance | Terms, licence, retention, withdrawal and controlled-data decisions | `blocked` | Publish only verified public/synthetic artefacts |
| Engineering | Clean builds, compatibility, documentation and independent reproduction | `partial` — local checks pass | Keep candidate unreleased |
| Security | Threat model, scans, SBOM, attestation and recovery evidence | `partial` — repository controls exist | Defer stable tag |
| Programme | Named primary/backup owners, support, succession, costs and host | `blocked` | Use time-limited interim ownership |
| Release | Immutable reviewed artefacts, manifest, checksums, citation and verification | `blocked` pending Tracks 013–016 | Do not tag or publish v1 |

For every closure, append the candidate commit, digest, reviewer role, decision
(`pass`, `revise`, `bounded` or `stop`), date and risk owner. Never overwrite a
prior decision; supersede it with a new versioned record.

The register is traceability scaffolding. Tracks 013–016 remain prerequisites,
so Track 017 remains Planned and stable v1.0.0 is not authorised.
