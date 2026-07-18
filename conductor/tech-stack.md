# Technical stack

## Architectural posture

- Public-data-first and metadata-first.
- Federated computation for controlled data.
- Language-neutral specifications with a Python reference implementation.
- Open, portable formats: CSV, JSON, YAML, Parquet and Arrow.
- Version every ontology, source release, transformation and model.

## Initial implementation

| Layer | Initial choice | Rationale |
|---|---|---|
| Language | Python 3.12+ | Broad scientific ecosystem and portability |
| Metadata | YAML validated by JSON Schema | Human-readable and machine-checkable |
| Tabular interchange | CSV initially; Parquet for larger releases | Accessible first, scalable later |
| Local analytics | DuckDB/Polars proposed for Track 002 | Reproducible analysis without a server |
| Statistical modelling | Python/R interfaces; Bayesian engine selected per demonstrator | Avoid premature lock-in |
| Reporting | Markdown and Quarto proposed | Reviewable source and reproducible outputs |
| Diagrams | Mermaid | Version-controlled architecture and workflows |
| Testing | pytest plus schema/fixture tests | Fast automated validation |
| Quality | Ruff, type checking and pre-commit proposed | Consistent contributions |
| CI | GitHub Actions | Portable public-repository automation |

## Data architecture constraints

- No controlled data leave approved environments unless explicitly permitted.
- No participant-level output is committed to Git.
- Small-cell and inferential disclosure rules are custodian-specific and must be encoded per node.
- Every transformed dataset must have a manifest, source checksum where lawful, and lineage record.
- Models must separate data, parameters, assumptions, code and outputs.

## Future-compatible standards

Candidate standards include ORPHAcodes/ORDO, ICD-10/11, SNOMED CT, MONDO, HPO, OMOP CDM, GA4GH standards, RO-Crate, Frictionless Data Packages, DataCite metadata and PROV-O. Adoption requires an explicit architecture decision record.
