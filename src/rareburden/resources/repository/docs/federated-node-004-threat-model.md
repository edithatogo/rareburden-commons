# Track 004 trust zones and threat model

This is a non-binding, offline design record. It does not authorise access to
custodian systems or controlled data.

| Zone | Contents | Permitted output |
|---|---|---|
| Coordinator | Versioned analysis and policy identifiers | Manifests and aggregate exports |
| Node boundary | Synthetic or custodian-local rows | Suppressed/released aggregates only |
| Review boundary | Export-review decision and correction record | Approved release metadata |

The primary adversaries are accidental participant-row leakage, small-cell
inference through repeated queries, credential disclosure in logs, and stale or
incorrect results being silently replaced. The local controls are fail-closed
field validation, minimum-cell suppression, bounded log redaction, immutable
superseding manifests, and major-version negotiation.

Local overrides may tighten a threshold or withdraw an output. They may not lower
the minimum-cell threshold, add participant identifiers, bypass version checks, or
replace a manifest in place. Custodian-specific rules and independent review are
external gates.
