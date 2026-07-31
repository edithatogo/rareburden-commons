# Technical stack

## Architectural posture

- Public-data-first and metadata-first.
- Federated computation for controlled data.
- Language-neutral contracts with a Python reference implementation.
- Open, portable formats: CSV, JSON, YAML, Parquet and Arrow.
- Version every ontology, source release, transformation, parameter, model and output.
- A static versioned release is the normative scientific product; hosted services are optional until separately governed.

## Target implementation stack

| Layer | v1 direction | Rationale |
|---|---|---|
| Language | Python 3.11–3.14 reference implementation | Compatibility with scientific and secure research environments |
| Packaging | Standard Python package, locked release environment and offline node bundle | Reproducibility and portability |
| Metadata | YAML/JSON validated by JSON Schema 2020-12 | Human-reviewable and machine-enforced contracts |
| Tabular interchange | CSV for small accessible releases; Parquet/Arrow for scale | Accessibility plus efficient exchange |
| Local analytics | DuckDB and/or Polars only after ADR and benchmark | Portable processing without mandatory server infrastructure |
| Statistical modelling | NumPy/SciPy plus a selected Bayesian engine per demonstrator where justified | Avoid premature framework lock-in |
| Reporting | Markdown and a reproducible static-report system | Reviewable sources and immutable products |
| Diagrams | Mermaid with accessible summaries | Version control and text alternatives |
| Testing | pytest, schema, property, contract, statistical, end-to-end and documentation tests | Scientific and software assurance |
| Quality | Ruff, static typing, coverage and compatibility tests | Stable public interfaces and maintainability |
| CI | GitHub Actions or equivalent with supported Python matrix | Portable automation |
| Release | Lockfile, SBOM, checksums/signing, provenance manifest and persistent archive | Supply-chain and scientific reproducibility |
| Federated node | Offline-capable package/container plus language-neutral schemas | Custodian-controlled execution |

## Data architecture constraints

- No controlled data leave approved environments unless explicitly permitted.
- No participant-level, row-level or small-cell output is committed to public Git.
- Custodian disclosure rules are authoritative and fail closed.
- Every transformed dataset has a manifest, source release/checksum where lawful and lineage record.
- Models separate data, parameters, assumptions, code and outputs.
- Source and ontology changes explicitly invalidate affected derived artefacts.
- A hosted API serves immutable reviewed releases, not mutable working tables.

## Compatibility target

- Linux on a current long-term-support distribution is the normative v1 platform.
- Python 3.11, 3.12, 3.13 and 3.14 are continuously tested on Linux.
- Python 3.13 is the cross-platform release/portability runtime; macOS and
  Windows candidate support is documented from actual test evidence in
  `../docs/supported-environments.md`. WSL remains unverified.
- Secure environments may use local runners that satisfy the versioned conformance contract.
- Stable schema, CLI and data-package changes follow `docs/release-policy.md`.

## Candidate standards requiring ADRs before adoption

ORDO/ORPHAcodes, ICD-10/11, SNOMED CT, MONDO, OMIM, HPO, OMOP CDM, GA4GH Data Use Ontology, RO-Crate, Frictionless Data Packages, DataCite metadata and PROV-O.
