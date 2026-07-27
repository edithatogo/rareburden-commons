"""Generate transparent source-access capability and evidence-gap maps."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


class GapMapError(ValueError):
    """Raised when a gap-map request cannot be classified."""


_ACCESS_TO_STATUS = {
    "open_download_api": "public_open",
    "public_web_registration": "public_registered",
    "controlled_research": "controlled_access_required",
    "federated_partner": "federated_analysis_required",
    "new_collection": "new_collection_required",
}
_STATUS_ORDER = {
    "public_open": 0,
    "public_registered": 1,
    "controlled_access_required": 2,
    "federated_analysis_required": 3,
    "new_collection_required": 4,
    "unavailable": 5,
}
_READINESS_ORDER = {
    "acquisition_tested": 0,
    "access_tested": 1,
    "metadata_reviewed": 2,
    "unverified": 3,
    "unavailable": 4,
}


def _verification_status(source: dict[str, Any], stage: str) -> str:
    verification = source.get("verification", {})
    record = verification.get(stage, {}) if isinstance(verification, dict) else {}
    return str(record.get("status", "not_tested")) if isinstance(record, dict) else "not_tested"


def _readiness(source: dict[str, Any]) -> str:
    if _verification_status(source, "acquisition_test") == "passed":
        return "acquisition_tested"
    if _verification_status(source, "access_test") == "passed":
        return "access_tested"
    if _verification_status(source, "metadata_review") in {"passed", "preliminary"}:
        return "metadata_reviewed"
    return "unverified"


def _matches_need(source: dict[str, Any], need: dict[str, Any]) -> bool:
    required_role = need.get("required_analytic_role")
    if required_role is not None and required_role not in source.get("analytic_roles", []):
        return False
    required_level = need.get("required_geographic_level")
    if required_level is not None and required_level not in source.get("geographic_levels", []):
        return False
    required_data_levels = need.get("required_data_levels")
    return not required_data_levels or source.get("data_level") in required_data_levels


def _validate_needs(needs: Any) -> list[dict[str, Any]]:
    if not isinstance(needs, list) or not needs:
        raise GapMapError("requirements.needs must be a non-empty list")
    validated: list[dict[str, Any]] = []
    seen_need_ids: set[str] = set()
    for index, need in enumerate(needs):
        if not isinstance(need, dict):
            raise GapMapError(f"requirements.needs[{index}] must be a mapping")
        required = {"need_id", "label", "domain", "scope"}
        missing = sorted(required - need.keys())
        if missing:
            raise GapMapError(f"requirements.needs[{index}] lacks {', '.join(missing)}")
        need_id = str(need["need_id"])
        if need_id in seen_need_ids:
            raise GapMapError(f"Duplicate need_id: {need_id}")
        seen_need_ids.add(need_id)
        validated.append(need)
    return validated


def build_domain_gap_map(catalog: dict[str, Any], requirements: dict[str, Any]) -> dict[str, Any]:
    """Classify data needs using access, capability and verification metadata.

    This remains a capability map.  A matching source does not establish analytical
    sufficiency, representativeness, transportability or permission for a specific use.
    """
    sources = catalog.get("sources", [])
    if not isinstance(sources, list):
        raise GapMapError("catalog.sources must be a list")
    title = requirements.get("title")
    if not isinstance(title, str) or not title.strip():
        raise GapMapError("requirements.title must be a non-empty string")
    needs = _validate_needs(requirements.get("needs"))

    active_sources = [
        source
        for source in sources
        if isinstance(source, dict) and source.get("status") not in {"blocked", "deprecated"}
    ]
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for source in active_sources:
        for domain in source.get("domains", []):
            by_domain[str(domain)].append(source)

    rows: list[dict[str, Any]] = []
    for need in needs:
        domain = str(need["domain"])
        candidates = by_domain.get(domain, [])
        matching = [source for source in candidates if _matches_need(source, need)]
        statuses = [
            _ACCESS_TO_STATUS[source["access_class"]]
            for source in matching
            if source.get("access_class") in _ACCESS_TO_STATUS
        ]
        status = min(statuses, key=_STATUS_ORDER.__getitem__) if statuses else "unavailable"
        readiness_values = [_readiness(source) for source in matching]
        readiness = (
            min(readiness_values, key=_READINESS_ORDER.__getitem__)
            if readiness_values
            else "unavailable"
        )
        tested = sorted(
            str(source["source_id"])
            for source in matching
            if _readiness(source) == "acquisition_tested"
        )
        access_tested = sorted(
            str(source["source_id"]) for source in matching if _readiness(source) == "access_tested"
        )
        metadata_only = sorted(
            str(source["source_id"])
            for source in matching
            if _readiness(source) in {"metadata_reviewed", "unverified"}
        )
        candidate_ids = sorted(str(source["source_id"]) for source in candidates)
        matching_ids = sorted(str(source["source_id"]) for source in matching)

        constraints: list[str] = []
        if need.get("required_analytic_role"):
            constraints.append(f"analytic role={need['required_analytic_role']}")
        if need.get("required_geographic_level"):
            constraints.append(f"geographic level={need['required_geographic_level']}")
        if need.get("required_data_levels"):
            constraints.append(
                "data level=" + "/".join(str(value) for value in need["required_data_levels"])
            )
        if matching_ids:
            rationale = (
                f"{len(matching_ids)} of {len(candidate_ids)} domain-matched source(s) satisfy the "
                "declared catalogue constraints. Access and test status do not establish "
                "fitness, completeness or representativeness."
            )
        elif candidate_ids:
            rationale = (
                f"{len(candidate_ids)} source(s) cover the domain, but none satisfy the declared "
                f"constraints: {', '.join(constraints) or 'unspecified capability constraints'}."
            )
        else:
            rationale = "No active source in the current catalogue is tagged for this domain."

        rows.append(
            {
                "need_id": need["need_id"],
                "label": need["label"],
                "domain": domain,
                "scope": need["scope"],
                "required_analytic_role": need.get("required_analytic_role"),
                "required_geographic_level": need.get("required_geographic_level"),
                "required_data_levels": need.get("required_data_levels", []),
                "status": status,
                "operational_readiness": readiness,
                "sufficiency": "not_assessed",
                "candidate_source_ids": candidate_ids,
                "matching_source_ids": matching_ids,
                "acquisition_tested_source_ids": tested,
                "access_tested_source_ids": access_tested,
                "metadata_only_source_ids": metadata_only,
                "country_specific_validation_required": True,
                "unresolved_questions": need.get("unresolved_questions", []),
                "rationale": rationale,
            }
        )

    return {
        "schema_version": "1.0.0",
        "map_type": "domain_access_capability",
        "title": title,
        "catalogue_schema_version": str(catalog.get("schema_version", "unknown")),
        "catalogue_last_updated": str(catalog.get("last_updated", "unknown")),
        "limitations": requirements.get("limitations", []),
        "summary": {
            "need_count": len(rows),
            "access_status_counts": dict(Counter(row["status"] for row in rows)),
            "readiness_counts": dict(Counter(row["operational_readiness"] for row in rows)),
        },
        "rows": rows,
    }


def render_gap_map_markdown(gap_map: dict[str, Any]) -> str:
    """Render the capability map as accessible Markdown."""
    lines = [
        f"# {gap_map['title']}",
        "",
        "> This is an access-capability map, not evidence that a source is complete,",
        "> representative, transportable or analytically sufficient.",
        "",
        f"Catalogue: schema `{gap_map['catalogue_schema_version']}`, updated "
        f"`{gap_map['catalogue_last_updated']}`.",
        "",
        "| Need | Domain | Scope | Access | Readiness | Matching sources |",
        "|---|---|---|---|---|---|",
    ]
    for row in gap_map["rows"]:
        sources = ", ".join(row["matching_source_ids"]) or "None matching"
        lines.append(
            f"| {row['label']} | `{row['domain']}` | {row['scope']} | "
            f"`{row['status']}` | `{row['operational_readiness']}` | {sources} |"
        )
    if gap_map.get("limitations"):
        lines.extend(["", "## Limitations", ""])
        lines.extend(f"- {item}" for item in gap_map["limitations"])
    return "\n".join(lines) + "\n"
