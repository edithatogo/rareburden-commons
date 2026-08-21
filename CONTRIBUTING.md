# Contributing

RareBurden Commons has one accountable human: repository owner and sole
maintainer `edithatogo`. Repository-owned review
uses role-separated agent panels and an attributable owner disposition; no
independent human, constituted-community or institutional approval is claimed
or required for repository work. Publisher, custodian and third-party rights
remain external facts and are kept fail-closed.

Agents, bots and external evidence providers are not maintainers, approvers or
accountable repository role-holders. A future human role requires an explicit
dated governance transition.

## Before proposing a change

1. Read `AGENTS.md` and the Conductor project context.
2. Check `conductor/tracks.md` and `conductor/roadmap.yml` for an existing work unit.
3. For a material feature, method, source adapter or governance change, create or update a track before implementation.
4. For a new data source, identify the exact parameter it supports, geographic granularity, representativeness, access route and licence state.
5. For a change affecting the stable product promise, update the roadmap or v1 acceptance evidence through formal change control.

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
make check
```

`make check` validates the catalogue, roadmap, track graph, tests, lint, repository safety and compilation.

## Track practice

- A track begins Planned, becomes Ready when dependencies and ownership are satisfied, and becomes Active when implementation begins.
- Plans are updated in the same commit as completed work.
- A track is not Complete until every required task is checked and `review.md` records findings and disposition.
- Unknown dependencies, cycles, release mismatches and incomplete completed tracks fail programme validation.

## Contributions to source and evidence metadata

A source entry must identify an official access route, access class, custodian, licence/terms, version strategy, geography level, intended analytic use, limitations and verification state. Do not include usernames, tokens, application identifiers or controlled metadata.

## Research and methods changes

Changes to disease inclusion, hierarchy, estimands, overlap rules, primary
models, economic perspective, uncertainty, transportability or release gates
require a decision record, an agent-panel challenge and an attributable owner
disposition. Do not describe the panel as independent approval.

## Commit and review practice

- Use a short-lived branch for a defined track.
- Make focused Conventional Commits.
- Include tests for executable changes.
- Describe provenance, uncertainty, privacy, security and backwards-compatibility implications in the pull request.
- Do not squash away important methodological or correction history merely for a shorter log.

## Prohibited content

Never commit identifiable or participant-level health data, small-cell outputs, data copied from controlled environments, credentials, private keys or source material whose terms prohibit repository storage.
