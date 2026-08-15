# Track 011 synthetic reference

`examples/analyses/bronchiectasis-synthetic.yml` is a non-binding assurance
specification for the rare-within-common workflow. It deliberately uses the
existing synthetic ledger identifiers and declares the result as
`synthetic_assurance`; it is not a bronchiectasis estimate.

The future RBC-P003 implementation must supply reviewed, setting-specific
parameters for cystic fibrosis, primary ciliary dyskinesia, immunodeficiency,
other causes, multi-aetiology overlap and unclassified causes. Those inputs must
carry age, geography, period, ascertainment and diagnostic-capacity context.

The fixture therefore tests the analysis contract while refusing to imply that
the synthetic fraction represents bronchiectasis aetiology. Clinical, methods,
patient/community and engineering review remain mandatory before activation.

## Bounded dependency reconciliation

The 2026-08-16 receipt at
`manifests/demonstrators/track-011-bounded-synthetic-receipt-2026-08-16.json`
binds exact synthetic artifacts from Tracks 008–010. Its denominator and all
component values are synthetic. Mutually exclusive categories are conserved
through the semantic aggregation contract; the multi-aetiology count is kept
outside those categories, and unknown and unaccounted quantities remain
visible. The implementation rejects activation flags, missing population
context and totals that exceed the denominator.

This is reproducible repository assurance only. It does not establish an
empirical bronchiectasis case definition, aetiologic composition,
transportability, clinical interpretation or a frozen RBC-P003 contract.
