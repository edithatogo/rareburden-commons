# Track 007 bounded pagination workflow

`scripts/capture_track_007_pages.py` captures a deterministic evidence record
for a bounded number of pages from supported public endpoints. It supports
GitHub repository search, Zenodo records and Hugging Face datasets. No
credentials are required.

Example:

```bash
uv run python scripts/capture_track_007_pages.py \
  --registry github \
  --query "rare disease burden" \
  --page-size 25 \
  --max-pages 4 \
  --output docs/track-007-live-pages-github-YYYY-MM-DD.json
```

The output path must be new; the command refuses to overwrite an earlier
capture. Inspect the result for the exact query, timestamp, endpoints, hashes
and stop reason before treating it as evidence. A failed HTTP response, invalid payload, changing declared total,
missing identifier or repeated identifier across pages stops the run.

The output distinguishes:

- `provider_total_reached`: the captured unique identifiers exactly equal the
  stable declared total and no provider cap applies;
- `short_page_observed` or `empty_page_observed`: the queried endpoint returned
  fewer results, without implying broader ecosystem completeness;
- `page_budget_reached`: the deliberate local bound was reached and uncaptured
  pages remain open;
- `provider_limited`: a documented provider result cap prevents exact capture
  of its declared total.

Even when `capture_complete_for_declared_total` is true, the claim is limited to
that endpoint, query and retrieval time. It is not evidence of comprehensive or
representative scholarly/repository coverage, novelty, protocol registration,
independent methods review or patient/community interpretation.
