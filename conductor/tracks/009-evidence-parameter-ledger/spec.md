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
