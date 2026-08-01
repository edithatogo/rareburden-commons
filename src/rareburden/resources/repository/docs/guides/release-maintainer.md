# Release maintainer guide

Use the [release policy](../release-policy.md), release-candidate checklist,
SBOM/checksum/provenance verifier and the exact locked environment. A release
candidate is not a stable release until every required review lane and release
authority decision is recorded.

Before publication, verify source, wheel, data-package and provenance-rich
artefacts from public instructions; retain hashes, attestations, environment
identity and correction/supersession links. Never publish credentials,
controlled data or unsupported empirical claims. Stable `v1.0.0` tagging is
reserved for Track 017 after its external gates pass.
