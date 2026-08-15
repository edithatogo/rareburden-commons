# Track 016 bounded retention and access policy

**Status:** operative for repository-owned synthetic/public preparation only;
production and controlled-data retention remain unauthorized.

This repository-owned policy applies to synthetic operational exercises and
offline release evidence. It does not authorise collection of participant,
controlled, credential or custodian-restricted data.

| Record class | Default retention | Access | Disposal/withdrawal |
|---|---:|---|---|
| Build manifests, checksums and provenance | release lifetime plus audit period | repository maintainers; read-only public release artefacts | supersede by immutable version; never rewrite history |
| Synthetic metrics and benchmark receipts | 12 months | maintainers and designated operator; aggregate only | delete source receipt on expiry; retain hash and disposition |
| Recovery/rollback exercise receipts | 24 months | security and operations roles; least privilege | redact before publication; retain disposition metadata |
| Incident records | case-dependent, minimum 24 months | incident lead and explicitly delegated responders | withdrawal requires closure authority and an audit entry |
| Credentials, tokens and secrets | zero in repository or receipts | secret manager only | revoke immediately on exposure; do not retain values |

Controls:

- access is role-based, time-bounded and logged;
- receipts contain hashes, status, measurements and redacted timestamps, not
  raw logs, environment secrets or personal data;
- deletion, correction and withdrawal create an append-only disposition record;
- a custodian's stricter policy overrides this draft;
- a named operational owner must approve any production retention exception.

The repository owner accepts this boundary for the bounded candidate. It does
not apply to production, hosted-service, participant-level, custodian-controlled
or controlled-data records. Those uses require a new exact-candidate policy and
authority disposition. The private backup-owner handoff remains incomplete and
cannot be inferred from this policy.
