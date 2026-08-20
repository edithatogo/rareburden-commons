# Track 016 support and security-fix policy

- **Policy date:** 2026-08-20
- **Status:** Owner-operated pre-release policy; backup continuity handoff
  incomplete
- **Scope:** Public repository code, documentation, schemas, synthetic fixtures
  and approved aggregate outputs

This policy defines the support and security-fix boundary that the sole
repository owner can operate now. It does not establish independent security
review, staffed support, production operations, controlled-data authorization
or a service-level commitment.

## Supported versions

| Surface | Fix status | Boundary |
|---|---|---|
| Current `main` branch | Eligible for security and privacy fixes | Pre-release, owner-operated and subject to available capacity |
| Immutable prerelease tags, including `v0.3.0-rc.2` | No continuing patch stream | A fix is released on a later reviewed commit or tag |
| Historical branches and older artefacts | Unsupported | May be withdrawn or superseded when affected |

Python 3.13 remains the release-build and cross-platform portability runtime.
The broader compatibility evidence and exclusions are defined in
[`supported-environments.md`](supported-environments.md). A runtime change
requires the repository's compatibility process and refreshed exact-candidate
evidence.

## Reporting channels

- Sensitive vulnerability, credential, privacy or exploit reports: use
  [GitHub private vulnerability reporting](https://github.com/edithatogo/rareburden-commons/security/advisories/new).
- Non-sensitive defects reproducible with synthetic or public inputs: use a
  public repository issue.
- If the private GitHub route is unavailable: contact repository owner
  `edithatogo` through an already established private channel. Do not place
  sensitive content in a public issue, pull request, commit or log.

GitHub private vulnerability reporting was observed enabled on 2026-08-20.
That is hosted platform state and must be rechecked when handling a report; the
repository document alone is not execution evidence for the external channel.

## Ownership and continuity

| Role | Current evidence state | Authority and limitation |
|---|---|---|
| Primary security, support and operations owner | `edithatogo` | May triage repository reports, freeze affected repository pathways, prepare fixes and record owner dispositions |
| Privacy-preserving backup role | `owner_attested_private_backup_acceptance` | Identity is not public; scope, escalation, expiry and hash-bound handoff evidence remain incomplete |

The backup role must not be described as continuity-ready until a stable
private role identifier, accepted support/incident/recovery/succession scope,
an escalation route, review or expiry date, and a hash-bound handoff exercise
are recorded. Owner-operated restore tests do not complete that handoff and do
not create independent operational evidence.

If the primary owner is unavailable before the handoff is complete, the safe
state is to keep production, controlled-data and stable-release pathways
disabled. No automatic authority transfers to an agent, contributor or
unverified contact.

## Triage and fix process

1. Preserve only the minimum privacy-safe report metadata and keep sensitive
   material out of public Git and logs.
2. Assess the affected commit, artefact, data boundary and downstream exposure.
3. Freeze affected acquisition, publication or release routes on credible
   critical impact, credential exposure, sensitive-data disclosure or integrity
   failure.
4. Prepare the smallest bounded fix on the current maintained branch, rotate
   exposed credentials outside Git where applicable, and run the repository's
   required validation.
5. Record correction, withdrawal, supersession or advisory evidence without
   publishing exploit-enabling or sensitive details.
6. Restore a disabled pathway only after the repository owner records an
   exact-candidate disposition and every applicable external authority remains
   satisfied.

No response-time, restoration-time, availability or service-level commitment
is made. Report receipt, severity assessment and fix timing depend on the sole
owner's available capacity. This limitation must be visible anywhere the
project's support posture is summarized.

## Evidence and claims boundary

Green CI, CodeQL, dependency review, Scorecard, SBOM and provenance checks show
that their configured controls ran on the referenced commit or artefact. They
do not prove continuous monitoring, staffed response, independent review,
backup continuity, production readiness or release authority.

The bounded policy publication can be recorded as complete while Track 016
remains Planned. It does not complete the separate qualifying backup handoff,
acceptance criterion 8, production operations, independent review or release
authority. Agent security/operator advice and the repository owner's
exact-candidate disposition remain separate evidence.
