# Stable v1 release evidence register

**Status:** preparatory; no release gate is passed by this document.  
**Revision:** 2026-08-01

This register indexes `docs/v1-acceptance-criteria.md`. A lane is `pass` only
when its artefact, validation result, reviewer decision and residual-risk owner
are recorded. Local checks do not substitute for independent or governance
evidence.

| Lane | Current state | Contingency |
|---|---|---|
| Scientific | `blocked` pending Track 013 | Remove unsupported comparative/global claims |
| Patient/community | `blocked` | Exclude patient-facing and policy claims |
| Data governance | `blocked` | Publish only verified public/synthetic artefacts |
| Engineering | `partial` — local checks pass | Keep candidate unreleased |
| Security | `partial` — repository controls exist | Defer stable tag |
| Programme | `blocked` | Time-limited interim ownership |
| Release | `blocked` pending Tracks 013–016 | Do not tag or publish v1 |

Record candidate commit, digest, reviewer, decision, date and risk owner for
each closure; supersede rather than overwrite prior decisions.
