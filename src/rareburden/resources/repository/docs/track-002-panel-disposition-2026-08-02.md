# Track 002 panel disposition — bounded source posture

**Decision state:** repository-owner approved bounded preparation posture
(2026-08-02); not scientific approval, custodian approval, licence
authorization, or production activation.

## Recommended posture (Option A)

- **Orphadata:** retain the same-date epidemiology and alignment XML pair as a
  candidate for disease metadata, prevalence/epidemiology attributes and
  identifier alignment. Do not use it as a denominator, DALY, mortality or
  causal-burden source.
- **UN WPP:** retain the compact WPP 2024 workbook as a candidate for explicit
  medium-variant national population denominators with bounded geography/year
  extraction. Do not interpolate age/sex or treat it as disease burden.
- **WHO GHE:** retain the pinned workbook as a candidate comparator for the
  year 2000 only. Do not represent it as a 2000–2021 series; exclude credited
  third-party fields unless separately cleared.
- **World Bank:** retain the bounded `SP.POP.TOTL` response as a probe and
  denominator cross-check. Do not silently mix it with WPP or activate it as a
  substitute without a precedence decision.

The repository owner approved this bounded posture. That approval narrows
implementation scope only; it does not satisfy the scientific, governance,
operator or Track 007 release gates.

## Conditions before any activation

1. Scientific authority confirms the estimand, metric, denominator, geography,
   time scope, limitations and acceptable use for each exact record.
2. Data-governance/custodian authority confirms terms, attribution,
   redistribution/cache posture, third-party material, retention and
   withdrawal/correction conditions.
3. A bounded source-change exercise demonstrates that changed bytes, changed
   terms, unavailable routes and checksum mismatches fail closed.
4. Receipts are bound to the exact source packet and manifest digest using the
   external gate receipt template.

## Governance posture (panel recommendation)

- Use ephemeral operator-side retrieval only while terms remain conditional;
  retain hashes, metadata and redacted manifests, not raw source bytes.
- Keep UN WPP and WHO GHE candidate-only until file/field-level terms permit
  the intended cache and derived-output use.
- Keep World Bank as a bounded probe; do not mirror or silently substitute it
  for WPP.
- Permit Orphadata-derived outputs only after confirming attribution,
  change-notice, third-party exclusions, retention and withdrawal handling.
- On terms or checksum drift, stop acquisition, emit a redacted
  `review_required` incident, quarantine newly fetched bytes under the local
  retention policy, and supersede the manifest rather than overwriting it.

## Contingencies

- If UN WPP terms or scope remain unclear, keep it candidate-only and use
  synthetic denominators; do not silently substitute World Bank.
- If WHO third-party permissions remain unclear, keep WHO manual and
  non-redistributed or defer it entirely.
- If Orphadata release pairing fails, retain identifier mapping only from a
  pinned ontology record or remain synthetic-only.
- If any reviewer disagrees with the metric/denominator interpretation, preserve
  both positions and narrow the supported claim until resolved.

The subagent panel prepared this recommendation; it cannot satisfy the
accountable scientific or data-governance gates.
