# Track 014 specification — Atlas, API and reproducible release engineering

## Objective

Publish reviewed aggregate evidence, estimates and gaps through accessible static products, a versioned API/data package and provenance-rich immutable releases.

## Required outputs

- atlas information architecture and user research;
- static country, disease-group, demonstrator and gap products;
- versioned aggregate data package and documented API;
- provenance and uncertainty display components;
- accessible text alternatives and non-colour-only visual design;
- release-manifest schema and build pipeline;
- citation metadata, checksums, licence inventory and RO-Crate or equivalent research object;
- immutable archive/DOI workflow;
- correction, withdrawal and supersession display;
- reproducible build from reviewed artefacts only.

## Acceptance criteria

1. Public products are generated from immutable reviewed releases, not mutable working data.
2. Every displayed estimate links to evidence status, source, uncertainty, quality and limitations.
3. Missingness is visible and not rendered as zero.
4. API and package versions follow compatibility policy.
5. Static and machine-readable products agree through automated tests.
6. Accessibility review and documentation tests pass.
7. Clean-environment build and independent reproduction succeed.
8. Release contents enforce third-party redistribution conditions.

## Non-goals

- a visually complete map achieved through unsupported estimates;
- mutable dashboards without archived releases;
- a public participant-level query interface;
- ranking countries without quality and uncertainty context.

## v1 contribution

This track provides the supported public product and release surface for V1-DOC, V1-REL and public-facing data criteria.
