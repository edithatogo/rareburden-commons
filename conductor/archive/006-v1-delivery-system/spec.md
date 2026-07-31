# Track 006 specification — v1 delivery system and foundation hardening

## Objective

Convert the foundation repository into a complete, machine-checkable Conductor delivery system with an explicit route to a stable, hardened and mature v1.0.

## Required outputs

- gate-based release roadmap from v0.2.0 to v1.0.0;
- complete track portfolio with specifications, plans, metadata, dependencies and target releases;
- maturity model and blocking v1 acceptance criteria;
- requirements traceability and programme risk register;
- release, compatibility and testing policies;
- formal review of Track 001;
- machine-readable roadmap and track-metadata schemas;
- automated roadmap/dependency validation;
- hardened local checks that work in Git clones and source archives;
- updated repository navigation, strategy and contributor workflow.

## Acceptance criteria

1. Every track in the roadmap has `spec.md`, `plan.md` and valid `metadata.json`.
2. Track dependencies are complete, reference existing tracks and contain no cycles.
3. Every track is assigned exactly once to a release from v0.1.0 to v1.0.0.
4. Stable v1.0 has objective, multi-domain blocking criteria.
5. Must requirements map to implementation tracks and evidence targets.
6. The roadmap validates offline through the CLI and CI.
7. `make check` includes linting and passes in both a Git clone and source archive.
8. Track 001 has a candid review and all known foundation gaps are assigned.

## Non-goals

- claiming that planned scientific or platform capabilities are already implemented;
- producing burden estimates in this planning release;
- assigning real partner endorsement or controlled-data access;
- weakening v1 criteria to fit existing code.

## v1 contribution

This track is the programme control plane. It makes the route, dependencies and stable-release definition auditable.
