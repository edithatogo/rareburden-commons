# Delivery workflow

## Work unit

Every material feature, dataset adapter, demonstrator or protocol revision is a **track** containing:

- `spec.md` — what and why, including acceptance criteria;
- `plan.md` — phases, tasks and verification;
- `metadata.json` — identifier, status, dates and dependencies.

## Branch and commit strategy

- Protect `main` once hosted.
- Use short-lived branches named `track/<id>-<slug>`.
- Make one focused commit per completed logical task.
- Use Conventional Commit prefixes: `docs:`, `feat:`, `fix:`, `test:`, `chore:`, `refactor:`.
- Update the track plan in the same commit as the work it records.
- Do not squash away evidence of important methodological decisions unless release policy later requires it.

## Definition of ready

A task is ready when scope, inputs, outputs, dependencies, privacy class and acceptance criteria are explicit.

## Definition of done

A task is done when:

1. its acceptance criteria are met;
2. automated checks pass where applicable;
3. provenance and limitations are documented;
4. no sensitive data are present;
5. the plan and track register are updated;
6. a focused Git commit records the change.

## Research workflow

1. Register the question and estimand.
2. Freeze disease and coding definitions.
3. Register eligible sources and access classes.
4. Extract or derive parameters with provenance.
5. Assess bias, transportability, overlap and uncertainty.
6. Run primary and sensitivity analyses.
7. Validate with independent sources and domain experts.
8. Apply disclosure review.
9. Release code, aggregate inputs where licensed, metadata and reproducible outputs.

## Review gates

- **Scientific:** estimand, case definition, bias, uncertainty and double counting.
- **Data governance:** licence, consent, custodian conditions and disclosure risk.
- **Patient/community:** relevance, framing, equity and acceptable use.
- **Engineering:** tests, reproducibility, dependency and security checks.

## Change control

Material changes to inclusion rules, burden definitions, ontology versions or economic perspective require an Architecture/Methods Decision Record in `docs/decisions/`.
