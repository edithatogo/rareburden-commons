# Python style guide

- Target Python 3.12 or later.
- Use type hints for public functions and dataclasses for stable records.
- Keep ingestion, transformation, modelling and presentation separate.
- Functions that transform data must be deterministic unless randomness is explicit and seeded.
- Raise actionable exceptions that identify source and validation field.
- Do not silently coerce disease codes, geography codes, dates or units.
- Add tests for schemas, edge cases, missingness and duplicate identifiers.
- Never print or log participant-level values.
