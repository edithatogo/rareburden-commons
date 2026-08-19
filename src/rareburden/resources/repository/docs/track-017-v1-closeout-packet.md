# Track 017 stable-v1 closeout packet

**Status:** non-binding preparation; stable-v1 publication remains disabled.

## Evidence lanes and decisions

| Lane | Required receipt | Accountable disposition |
|---|---|---|
| Documentation and accessibility | Two role-separated usability-agent reports, task outcomes, accessibility findings and remediation log | repository owner: accept, revise, defer or stop |
| Reproduction | Two clean builds and separately recorded owner-operated clean-environment reproduction | repository owner: pass, qualify, revise or fail |
| Ownership and sustainability | Named owner, exact backup-role evidence, incident scope, succession and cost model | repository owner: accept, bound or defer |
| Scientific and governance | Linked dispositions from Tracks 002–016, agent-panel dissent and residual-risk register | repository owner: accept, narrow, revise, defer or stop |
| Release integrity | Exact tag, source/data/provenance checksums, SBOM, attestation and public-artifact verification | release authority: release, bounded, revise or stop |

## Receipt contract

Every receipt must identify the candidate tag or commit, input/release digest,
environment, commands, UTC timestamp, outputs, discrepancies, reviewer role and
decision expiry. Agent panels are advisory and must not be described as
independent, human, patient/community, custodian, licensor, institutional or
external approval. Owner-operated reproduction is repository evidence, not an
independent-operator receipt. The reported backup acceptance remains an owner
attestation until the continuity fields in ADR-0009 are recorded.

## Safe continuation

Continue offline tutorial, documentation-link, release-manifest and negative
gate tests. Keep `v1.0.0` tagging, public stable-release claims and support
promises disabled until every lane has an accountable disposition.
