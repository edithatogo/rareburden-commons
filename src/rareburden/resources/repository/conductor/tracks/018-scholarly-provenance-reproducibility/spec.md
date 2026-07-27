# Track 018 specification — Scholarly provenance, protocol transparency and reproducibility

## Objective

Make every supported scientific release auditable from immutable source identity through each transformation activity to the reported result, while distinguishing internal reproducibility evidence from independent reproduction and external replication.

## Why this track exists

A checksum on a final table is not sufficient scholarly provenance. Reviewers need to know what was planned, what actually ran, which exact bytes and software were used, what decisions or deviations occurred, how uncertainty was generated, and whether another operator has reproduced the work. The project must expose these facts without fabricating preregistration, DOI, peer-review or external-validation claims.

## Scope

- content-addressed protocol snapshots and explicit internal-freeze versus external-preregistration status;
- timing-classified analytic decisions, amendments and deviations;
- immutable activity-level transformation records;
- workflow dependency graphs derived from exact producer-consumer artefact identities;
- W3C PROV-O JSON-LD projection while retaining native records as normative;
- closed-lineage audit and fail-closed release checks;
- RO-Crate and Process Run Crate-compatible research-object packaging;
- GATHER evidence mapping for health-estimate reporting;
- CodeMeta, Citation File Format, Zenodo and DataCite-ready scholarly metadata;
- conservative, machine-readable reproducibility maturity assessment;
- package verification from disk rather than trust in declared metadata.

## Required outputs

- schemas, builders and verifiers for protocol registrations, decision logs, transformation runs, workflow runs, PROV bundles, lineage audits, reporting checklists and reproducibility assessments;
- a self-contained synthetic reference research object;
- exact source, dependency, environment, random-state and release identity;
- tests for tampering, missing evidence, path escape, content drift and unsupported maturity claims;
- standards and limitation documentation;
- a roadmap connection from structural auditability to independent reproduction and external empirical replication.

## Acceptance criteria

1. The reference workflow records prospective and retrospective evidence separately.
2. Every computational activity has exact input and output hashes, software identity, environment, parameters, command and timing.
3. The workflow graph is derived from content-identical producer-consumer relations and has no ambiguous producers or cycles.
4. Native provenance and the W3C PROV-O projection are independently integrity checked.
5. The release research object contains the source snapshots, protocols, schemas, data fixtures, transformation evidence, results, limitations and reporting evidence needed for offline audit.
6. Protocol status cannot be described as externally preregistered without a persistent external registration URL.
7. Post-hoc decisions require evidence and deviations cannot be silently omitted.
8. Internal structural assessment cannot claim independent reproduction or external replication.
9. Tampering with protocol bytes, provenance relations, release artefacts or maturity evidence is detected.
10. The synthetic reference package validates without network access and makes no empirical burden claim.

## Non-goals

- claiming that standards alignment proves scientific validity;
- claiming independent reproduction before a separate operator completes it;
- inventing persistent identifiers, preregistrations, repository deposits or external reviews;
- treating RO-Crate, PROV-O or GATHER as substitutes for methods review;
- publishing restricted source data in a research object.

## v1 contribution

This track supplies the scholarly assurance substrate for V1-DATA-01 to V1-DATA-03, V1-SCI-05, V1-ENG-03 to V1-ENG-05, V1-DOC-05 and V1-REL-01 to V1-REL-03. Tracks 013, 014 and 017 remain responsible for independent reproduction, external validation, public deposition and stable-release approval.
