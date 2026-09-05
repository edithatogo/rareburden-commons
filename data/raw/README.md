# Medallion raw / bronze boundary

The medallion system explicitly includes a raw (bronze-ingest) stage, but raw
bytes are held in governed private staging outside this public Git repository.
The repository stores the intake manifest, source version, retrieval evidence,
hashes, licence assessment, and reproducible transformations; it may store
lawfully redistributable aggregate derivatives only after their terms have been
checked.

This directory is intentionally excluded from Git except for this notice. Do
not place controlled, patient-level, small-cell, confidential, or licensed
source data in the repository. A raw source is not public merely because its
web page is publicly reachable: redistribution rights must be established for
the exact artifact and intended use.

See `docs/source-acquisition-assessment-2026-09-04.yml` for the current
source-by-source evidence and disposition.
