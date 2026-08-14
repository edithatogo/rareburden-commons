# Developer guide

Read `AGENTS.md`, `conductor/workflow.md` and the active track before changing
the repository. Keep the data path explicit:

`provider -> NormalizedInputBundle -> prepare_analysis_inputs -> ValueArray/ParameterSet`.

Add focused tests for behavioural changes, preserve provenance and privacy
boundaries, run `uv run make check`, and make a focused Conventional Commit.
Do not add controlled data, credentials or claims of external validation.

Use the schemas and existing scripts as the contract. A passing local test is
repository evidence only; hosted checks, independent review and release
authority remain separate gates.
