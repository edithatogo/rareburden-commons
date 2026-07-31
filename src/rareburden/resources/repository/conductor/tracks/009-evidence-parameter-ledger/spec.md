# Track 009 specification — Evidence and parameter ledger

## Objective

Create the machine-readable evidence core that links each analytic parameter to its population, source, uncertainty, quality, transportability, assumptions and permitted use.

## Required outputs

- parameter, evidence-assessment, analysis-specification and assumption schemas;
- stable identifiers and immutable revision history;
- support for observed, transformed, synthesised, transferred, modelled and assumed status;
- population, geography, period, disease, measure, metric and unit contracts;
- quality, bias and transportability assessment model;
- provenance links to source-release and transformation manifests;
- query and validation utilities;
- release blockers for incomplete mandatory evidence;
- fixtures representing conflicting, missing and non-transportable evidence.

## Acceptance criteria

1. Every model input and public estimate resolves to one or more ledger records.
2. Units, populations and time periods cannot combine silently when incompatible.
3. Quality and transportability judgements record rationale and reviewer.
4. Assumptions are distinguishable from empirical parameters in machine and human outputs.
5. Revision history preserves prior released values and their downstream impact.
6. Missing mandatory provenance, uncertainty or evidence status blocks release.
7. Ledger exports remain portable and schema-versioned.

## Non-goals

- treating a quality score as a substitute for expert judgement;
- automatically selecting one estimate from conflicting evidence without rules;
- storing controlled participant records;
- erasing superseded evidence from release history.

## v1 contribution

This track is the provenance and parameter substrate for V1-SCI-03, V1-DATA-03, V1-DATA-06 and V1-DATA-07.

## Non-binding protocol draft — ledger contract v0.1.0 (2026-07-27)

Preparatory only; this does not activate the track or freeze the v0.4 schema. Each parameter records stable ID/revision, supersession, quantity type, population/geography/period, measure, metric, unit, semantic IDs, source release, transformations, evidence status, quality, bias, transportability, licence, uncertainty and rationale. The workflow validates lawful acquisition outputs, rejects missing mandatory fields, preserves conflicts/missingness, supports historical queries and traces downstream impact. Epidemiology, data-governance, engineering and methods review are required.
