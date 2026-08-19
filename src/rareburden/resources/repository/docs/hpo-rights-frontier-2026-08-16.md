# HPO exact-asset rights frontier

The authoritative HPO repository points to an HPO licence page. Its current
`hpo.jax.org/app/license` target returned 404 on 2026-08-16, but the official
HPO GitHub Pages predecessor remains available at
`https://human-phenotype-ontology.github.io/license.html`. The exact observed
HTML is 8,351 bytes with SHA-256
`d63799ff8d381891114b22e78c8164f198a9642f9ed0ca8b53bc73238c318b39`
and HTTP `Last-Modified: 2018-06-21T09:11:32Z`.

That page states that its restrictions apply to every file provided by the HPO
project, permits downloading and using HPO files, and expressly anticipates
public display when the HPO Consortium is acknowledged, the relevant date or
version is shown, and content and logical relationships are unaltered. The
bounded archive therefore permits only exact, version-labelled publisher bytes
for core ontology assets: `hp`, `hp-base`, and `hp-simple-non-classified` in
JSON, OBO and OWL forms. The archive records attribution and a no-modification
statement. This is a repository disposition, not legal advice.

The same general licence text does not eliminate embedded-source uncertainty.
`hp-full` merged imports remain metadata-only. Disease, gene, phenotype and
annotation mappings remain metadata-only because they may encode OMIM,
Orphanet or other source relationships. International/French and repository
translation files remain metadata-only because the current official
translation repository has neither a licence file nor tags; an MIT licence in
the separate historical `drseb/HPO-translations` repository is not imputed to
the current repository.

The per-asset matrix covers all 707 release assets observed in the bounded
GitHub release inventory. Of these, 288 core ontology assets are eligible for
exact public archival and 419 remain metadata-only. The manual Actions workflow
processes at most ten assets and 1 GB per run, streams through temporary runner
storage, verifies publisher size and any available GitHub SHA-256, skips an
already-present matching remote path, and fails on drift or conflict. It does
not establish history outside the observed GitHub endpoint or clinical fitness.
