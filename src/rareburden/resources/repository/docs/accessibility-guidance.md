# Accessibility guidance for public artefacts

This guidance is a repository-owned preparation aid. It does not constitute an
external accessibility audit or establish that an atlas, API, or other product
is ready for release.

## Required presentation rules

- Provide a plain-language summary and a structured text table for every chart,
  map, or visual summary. The table must preserve units, missingness,
  suppression, uncertainty, and the evidence status of each value.
- Do not use colour as the only way to communicate a category, warning,
  confidence level, or missing value. Pair colour with text, labels, symbols,
  or table columns, and ensure the distinction remains understandable in
  greyscale.
- Keep headings, table headers, link text, and form labels meaningful when
  read out of context. Do not use bare “click here” links.
- Preserve a logical heading order and a keyboard-operable reading order in
  rendered products. Interactive controls require visible focus and a text
  label or accessible name.
- Expose missing, suppressed, and unavailable values explicitly (for example,
  `null` with a reason) rather than silently substituting zero or an empty
  string.

## Review evidence

For each release candidate, record the rendered artefact, commit, tool or
checker version, viewport or assistive-technology context, findings, and
disposition. A local checklist or passing automated check is preparatory
evidence only; the Track 014/017 accessibility gate remains open until the
release authority records its decision.

## Fallback

If an interactive or hosted product cannot satisfy these rules, publish only
the reviewed static and machine-readable aggregate pair with the structured
text alternative. Keep the interactive/API surface documented but inactive.
