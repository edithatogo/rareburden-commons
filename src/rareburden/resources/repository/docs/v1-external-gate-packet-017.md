# Stable v1 external-gate packet

**Status:** request packet; no gate is approved by this document.  
**Revision:** 2026-08-01

Each gate requires a dated decision, named reviewer or authority, exact
candidate commit/artefact digest, residual risks and an attached receipt.

| Gate | Decision required | Minimum evidence | Safe fallback |
|---|---|---|---|
| Scientific | Approve, revise or bound estimands and interpretations | Independent methods review, triangulation and sensitivity disposition | Remove unsupported comparative/global claims |
| Patient/community | Acceptable use, harms, equity and framing | Recorded review, dissent/disposition and participation record | Exclude patient-facing and policy claims |
| Data governance | Terms, retention, withdrawal and disclosure authority | Source/licence decisions and custodian conditions | Public/synthetic artefacts only |
| Engineering | Independent reproducibility and support scope | Clean-clone transcript, two candidate digests and reproduction report | Keep release candidate unreleased |
| Security | Operational risk acceptance | Threat-model review, scans, SBOM, attestation and recovery exercise | Defer stable tag |
| Programme | Accept owners, succession and operating costs | Primary/backup roster, approved cost model and host decision | Time-limited interim ownership with reduced scope |
| Release | Authorise tag and publication | Final criterion table, immutable manifest, archive and public verification | `revise` or `bounded`; no v1 tag |

Do not treat a green local test, draft protocol, invitation, proposed partner or
maintainer-only run as external evidence. Append receipts to the versioned
evidence register and supersede, rather than overwrite, prior decisions.
