# Supported environments

**Evidence date:** 1 August 2026
**Scope:** pre-release reference implementation and synthetic/offline assurance;
not a controlled-node accreditation or service-level commitment.

## Runtime matrix

| Environment | Evidence level | Supported scope |
|---|---|---|
| Ubuntu hosted runner, Python 3.11–3.14 | Continuously tested | Full offline programme, schema, workflow, lock, type, lint and unit checks |
| Ubuntu hosted runner, Python 3.13 | Release candidate | Coverage, reproducibility, deterministic distributions, installed-wheel execution, SBOM and clean network-disabled node installation |
| macOS hosted runner, Python 3.13 | Portability candidate | Programme/tests, installed wheel and clean network-disabled synthetic node installation |
| Windows hosted runner, Python 3.13 | Portability candidate | Programme/tests, installed wheel and clean network-disabled synthetic node installation |

Linux on a current GitHub-hosted Ubuntu image is the normative pre-release
platform. Python 3.11 through 3.14 are supported for the pure-Python reference
package. Python 3.13 is the release-build and cross-platform portability runtime.
The exact dependency set is `uv.lock`; production and development exports are
hash-pinned in `requirements.txt` and `requirements-dev.txt`.

## Evidence and limits

PRs #23–#25 passed the protected matrix on exact heads, including CodeQL,
dependency review, Python 3.11–3.14, full distribution assurance and
Ubuntu/macOS/Windows portability. The three platform jobs staged locked wheels,
disabled package indexes during clean installation and ran the synthetic node
from an unrelated directory.

These hosted runners are candidate engineering evidence. They are not a
custodian environment, a genuinely independent operator, a controlled-data
pilot, or a promise that every secure research environment supports the package.
WSL, containers, Linux ARM64, macOS x86_64 and Python versions outside the table
are not currently supported claims. A local environment must satisfy the
versioned schemas, locked dependency and offline conformance gates before use.

## Compatibility and change control

- Patch/minor runtime support changes require the complete protected matrix.
- Removing a supported Python version or changing the normative platform follows
  the compatibility and deprecation process in `docs/release-policy.md`.
- Native dependencies or a container runtime require an ADR plus cross-platform
  and offline evidence before adoption.
- Controlled-node activation additionally requires Track 004 custodian,
  governance, privacy, security and independent-operation evidence.
