# Data-source catalogue

`data_sources.yml` is the first machine-readable inventory of candidate evidence sources and access routes. It records discovery metadata only; it contains no credentials, downloaded source data or claim of partnership.

Validate it from the repository root:

```bash
python -m rareburden validate-catalog
```

A source marked `approved` has passed only the foundation metadata review. It is not necessarily approved for a specific analysis, and its licence and release must be rechecked at acquisition time.
