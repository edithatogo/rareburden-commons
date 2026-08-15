# HPO historical archive frontier

The official GitHub release API was exhaustively paginated on 2026-08-16 for
`obophenotype/human-phenotype-ontology`. The bounded observation contains 64
releases and 707 release assets from `v2017-03-09` through `v2026-06-23`. The
existing byte manifest covers 15 of those releases and 320 assets. The other 49
release tags are an explicit historical preservation gap, not evidence that no
older HPO material exists outside GitHub releases.

The repository `LICENSE.md` redirects to an unavailable website route and the
GitHub licence classifier reports `NOASSERTION`. Consequently this change
archives factual release metadata only. It does not publish another copy of any
HPO release asset. Exact asset-level redistribution terms must be recorded
before `archive_route` can change from `metadata_only`.

The official `hpo-translations` repository has no GitHub releases or tags and no
repository licence file. Its `main` history observation contains 128 commits and
16 language codes discoverable from Babelon/XLIFF/documentation paths. The
owner's existing public fork and previously prepared translation Git bundle are
therefore reused rather than duplicated. Translation bytes remain disabled
pending an exact licence; the manifest records the observed head and history
boundary without claiming all-time or language completeness.

The manual Actions audit is intentionally metadata-only, bounded to five
minutes, publishes the two validated manifests under `registry/hpo/` in the
existing public `edithatogo/dataset-estate-registry`, and produces a validation
receipt. It refuses a private destination and never uploads source bytes. A future byte continuation must be
separate, hash-deduplicated against the existing 15-release manifest and remote
receipts, limited by artifact/byte/time budgets, and enabled only after exact
rights are affirmative.
