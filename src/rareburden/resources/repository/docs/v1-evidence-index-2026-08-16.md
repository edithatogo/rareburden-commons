# Stable-v1 evidence index status

The machine-readable index at
`manifests/release/v1-evidence-index-2026-08-16.json` enumerates all 67
criteria in `docs/v1-acceptance-criteria.md`, binds the current repository
evidence by SHA-256 and records an explicit gap for every criterion group.

“Index complete” means every criterion is accounted for. It does **not** mean
the criteria are satisfied or that stable release is authorized. Every
criterion remains fail-closed for the exact v1 release decision because the
repository has bounded synthetic/repository evidence rather than a frozen v1
candidate disposition.

The repository owner has now recorded a bounded synthetic/public-preview
decision for exact candidate `ba92940572bd69e19d54447e59b8ba8f776e3d5b`;
stable release is explicitly deferred. Two actions remain outside this indexing
task:

1. qualifying backup-continuity evidence beyond the owner's private-role
   attestation;
2. publication and verification of stable public artifacts, which can occur
   only after that decision.

The index validator rejects missing, duplicated or reordered criteria, stale
hashes, unbound evidence, closed stable criteria, or any release/authority
claim. No tag, publication, support promise or backup-continuity claim is made.
