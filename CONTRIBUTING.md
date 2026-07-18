# Contributing

RareBurden Commons is intended to become a multidisciplinary public-good project. The foundation is not yet a constituted consortium, so contribution processes will evolve with patient/community and institutional governance.

## Before proposing a change

1. Read `AGENTS.md` and the Conductor project context.
2. Check `conductor/tracks.md` for an existing work unit.
3. For a material feature or method change, create or request a track before implementation.
4. For a new data source, identify the exact parameter it can support and its access/licence route.

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
make check
```

## Contributions to the source catalogue

A source entry must include an official access URL, access class, custodian, licence statement, version strategy, intended analytic use, material limitations and a recent verification date. Do not include usernames, tokens, application identifiers or controlled metadata.

## Research and methods changes

Changes to disease inclusion, hierarchy, estimands, overlap rules, primary models, economic perspective or release gates require a decision record and review by the future scientific and patient/community governance processes.

## Commit and review practice

- Use a short-lived branch for a defined track.
- Make focused Conventional Commits.
- Update the active plan with completed work.
- Include tests for executable changes.
- Describe provenance, uncertainty, privacy and backwards-compatibility implications in the pull request.

## Prohibited content

Never commit identifiable or participant-level health data, small-cell outputs, data copied from controlled environments, credentials, private keys or source material whose terms prohibit repository storage.
