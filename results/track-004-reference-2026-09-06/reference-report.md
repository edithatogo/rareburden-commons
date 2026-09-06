# Protocol RBC-F001 Bounded Federated Node Reference Report

**Date:** 2026-09-06  
**Track:** 004-federated-node-runner  
**Protocol:** RBC-F001 v0.2.0-bounded  
**Lifecycle Status:** Complete (bounded synthetic federated node package; no live custodian linkage)  
**Sole Accountable Human:** `edithatogo` (repository owner)  

---

## 1. Executive Summary

Under Protocol RBC-F001, the federated country-node package has been validated for
bounded synthetic offline execution without network dependencies or live hospital linkage:
- **Offline Cohort Analysis**: Evaluated across deterministic synthetic cohorts with zero participant identifiers.
- **Statistical Disclosure Control**: Minimum cell suppression (k=5) enforced; sensitive fields rejected.
- **Durable Store Mechanics**: Append-only transactional policy store verified with tamper checks and hash chains.
- **Execution Preflight**: Semantic version compatibility and deterministic execution manifests verified.
- **Owner-Operated Clean Rehearsal**: Offline installation and execution validated from clean worktree with locked wheels.

---

## 2. Gate Verification Summary

| Gate ID | Category | Status | Evaluation |
|---|---|---|---|
| `rights_and_data_use_contract` | governance_assurance | pass_bounded | verified_bounded_synthetic |
| `common_analysis_contract_and_locked_wheels` | packaging_and_dependencies | pass_bounded | verified_bounded_synthetic |
| `durable_policy_and_query_store` | security_and_provenance | pass_bounded | verified_reference_primitive |
| `clean_environment_installation_rehearsal` | operational_verification | pass_bounded | verified_owner_operated |
| `multi_lane_advisory_review` | review_and_disposition | pass_bounded | verified_advisory_panel |
| `bounded_node_package_release` | release_authorization | pass_bounded | verified_bounded_disposition |

---

## 3. Preserved Boundaries & Continuous Guarantees

- **Controlled Data Pilots:** Bounded post-v1 under ADR-0005. No clinical data accessed.
- **Custodian Store Authority:** Local SQLite primitives provide reference append-only behavior; hospital database authority remains external.
- **Sole Accountable Human:** Sole human governance anchored in `edithatogo` under ADR-0011.
- **Advisory Role Separation:** Agent panels provide advisory challenge under ADR-0009 without claiming independent certification.
