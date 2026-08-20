# Release and compatibility policy

## Version domains

RareBurden Commons versions different objects independently:

- **software:** semantic versioning, for example `1.2.0`;
- **schemas:** semantic version and immutable schema identifier;
- **protocols:** protocol identifier plus major/minor revision, for example `RBC-P001 v1.1`;
- **source releases:** custodian version plus RareBurden acquisition manifest;
- **analytic releases:** immutable release identifier linking code, data manifests, parameters and outputs;
- **atlas/API:** API and data-package versions with documented compatibility.

A software version does not silently imply that protocol, schema or data versions are unchanged.

## Release channels

| Channel | Intended use | Stability promise |
|---|---|---|
| Development snapshot | Internal integration and review | None |
| Alpha (`0.x` early) | Method and interface exploration | Breaking change permitted with changelog |
| Beta (`0.x` later) | External validation of substantially complete scope | Breaking change requires migration guidance |
| Release candidate | Stable-scope verification | Only release-blocking fixes unless the candidate is reset |
| Stable (`1.x`) | Supported public use | Semantic compatibility and published support policy |

## Semantic-version rules

- **Major:** incompatible public API, schema or interpretation change.
- **Minor:** backwards-compatible capability or dataset addition.
- **Patch:** backwards-compatible defect, documentation, security or correction release.

Scientific corrections that materially alter published estimates must receive a new analytic release even when no software code changes.

## Compatibility commitments from v1.0

- Public schemas are not changed incompatibly within the same major version.
- Deprecated fields remain readable for at least one subsequent minor release unless a security or legal issue requires immediate removal.
- Schema migrations are executable and tested against representative historical fixtures.
- CLI removals and behaviour changes are announced in the changelog and migration guide.
- Node packages declare compatible coordinator, schema and protocol versions before execution.

## Release contents

A supported release contains, as applicable:

- source archive and complete Git history reference;
- locked dependencies and supported runtime matrix;
- checksums and build provenance;
- software bill of materials;
- machine-readable release manifest;
- protocol and schema versions;
- source-release and acquisition manifests;
- lawful aggregate inputs or retrieval instructions;
- tests and verification command;
- methods, limitations and quality report;
- citation and licence metadata;
- correction, withdrawal and support instructions.

## Release process

1. Freeze scope and create a release-candidate branch or immutable commit.
2. Run the role-separated agent panels (programme, methods, rights/data-use,
   community/harm, engineering and security) and record the accountable
   owner disposition. No independent or human approval is implied.
3. Build from a clean environment using locked dependencies.
4. Run the full test, documentation, security, reproducibility and performance suites.
5. Generate release manifests, checksums, SBOM and provenance attestations.
6. Run a separately executed owner-operated reproduction of the reference
   analysis and label it repository evidence, not independent reproduction.
7. Review public outputs for disclosure, accessibility and claims with the
   agent panels and owner.
8. Record the release decision and residual risks.
9. Tag, archive and publish immutable artefacts.
10. Verify the published artefacts using the public instructions.

## Corrections and withdrawals

Corrections are classified as:

- **documentation-only:** meaning unchanged;
- **metadata:** provenance or descriptive fields corrected;
- **analytic:** inputs, mappings, parameters or code alter estimates;
- **privacy/security:** material must be restricted, withdrawn or rotated;
- **interpretive:** conclusions or policy framing require correction.

Analytic and interpretive corrections receive a public notice describing affected releases, magnitude, cause and replacement. Privacy or legal incidents may require immediate withdrawal before a complete notice is available.

## Support policy

Before v1.0, only the current development line is supported. At v1.0, the project will publish:

- supported software and schema versions;
- security-fix responsibility;
- deprecation window;
- response and escalation process without promising unstaffed service levels;
- end-of-support criteria;
- process for transferring maintenance if ownership changes.

## Rollback

Every release process must preserve the ability to:

- restore the last known-good public artefacts;
- identify all outputs derived from an affected source, parameter or code version;
- disable a compromised adapter or node package;
- publish a correction without rewriting prior history;
- notify known downstream users where contact is available.
