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
