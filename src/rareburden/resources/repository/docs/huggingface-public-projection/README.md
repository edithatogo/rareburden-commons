---
pretty_name: RareBurden Commons Open Source Snapshots
license: other
task_categories:
- other
tags:
- rare-disease
- ontology
- public-health
- population
---

# RareBurden Commons open source snapshots

This public preservation projection contains exact, hash-bound source files
whose observed terms affirmatively permit redistribution. Each source retains
its own licence; `license: other` is intentionally used because the collection
is not governed by one uniform licence.

Included:

- Orphadata July 2026 alignment and epidemiology files — CC BY 4.0.
- Exact MONDO release assets — CC BY 4.0. The currently receipt-bound history
  covers `v2026-08-04`, `v2026-07-06`, `v2026-06-02`, `v2026-05-05`,
  `v2026-04-07`, `v2026-03-03`, `v2026-02-03`, `v2026-01-06` and
  `v2025-12-02` through `v2025-06-03`; this is a bounded frontier, not a
  completeness claim.
- UN World Population Prospects 2024 demographic indicators workbook —
  CC BY 3.0 IGO, excluding any third-party classifications.
- A bounded World Bank Indicators API response — CC BY 4.0 for the observed
  series; retained as a probe and never substituted for WPP.

The `notices/` directory contains source-specific attribution, scope,
change-status and no-endorsement notices. `SHA256SUMS` binds the original
projection; later exact-byte batches are bound by reviewed per-object SHA-256
receipts in the canonical governance repository. Inclusion does not activate a
RareBurden estimand and makes no clinical, diagnostic, completeness,
representativeness or endorsement claim.

Not included: WHO GHE bytes, HPO assets without exact affirmative terms,
either national PanelApp dataset, UMLS, OMIM, SNOMED CT,
controlled-environment data, or any source without affirmative redistribution
evidence.

Canonical governance and provenance live at
https://github.com/edithatogo/rareburden-commons. The mixed-rights
`hpo-licensed-ontology-archive` remains private and must not be made public as
a whole.
