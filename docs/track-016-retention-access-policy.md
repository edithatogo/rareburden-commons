# Track 016 retention and access policy (draft)

This repository-owned draft applies to synthetic operational exercises and
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

This is a proposed control boundary. It becomes operative only after security,
data-governance and named-owner acceptance are recorded in the Track 016 review
packet.
