"""Machine-readable reporting-guideline evidence for health estimates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from rareburden.provenance import content_id

GATHER_SOURCE = "https://www.who.int/publications/m/item/gather-checklist"
GATHER_ITEMS: tuple[tuple[int, str, str], ...] = (
    (1, "Objectives and funding", "Define indicators, populations and time periods."),
    (2, "Objectives and funding", "List funding sources."),
    (3, "Data inputs", "Describe how data were identified and accessed."),
    (4, "Data inputs", "Specify inclusion, exclusion and ad-hoc exclusions."),
    (5, "Data inputs", "Describe included data sources and key characteristics."),
    (6, "Data inputs", "Identify important potential biases in input-data categories."),
    (7, "Data inputs", "Describe and source other analysis inputs."),
    (8, "Data inputs", "Provide extractable inputs and metadata, or identify custodians."),
    (9, "Data analysis", "Provide a conceptual overview of the analysis."),
    (10, "Data analysis", "Describe all analysis steps and mathematical methods."),
    (11, "Data analysis", "Describe candidate-model evaluation and final selection."),
    (12, "Data analysis", "Report model-performance and sensitivity evaluations."),
    (13, "Data analysis", "Describe uncertainty methods and omitted uncertainty sources."),
    (14, "Data analysis", "State how analytic source code can be accessed."),
    (15, "Results and discussion", "Provide estimates in an extractable format."),
    (16, "Results and discussion", "Report quantitative uncertainty."),
    (17, "Results and discussion", "Interpret results against existing evidence and revisions."),
    (18, "Results and discussion", "Discuss assumptions and data or model limitations."),
)


class ReportingChecklistError(ValueError):
    """Raised when reporting evidence is incomplete or misleading."""


def build_gather_checklist(
    *,
    report_id: str,
    title: str,
    created_at: str,
    evidence: Mapping[int, Mapping[str, Any]],
    scope_statement: str,
) -> dict[str, Any]:
    """Build a content-addressed GATHER evidence checklist.

    Checklist wording is concise rather than normative; ``source`` identifies the official
    checklist.  Every item must be classified explicitly, preventing silent omissions.
    """
    expected_ids = {item_id for item_id, _, _ in GATHER_ITEMS}
    supplied_ids = set(evidence)
    if supplied_ids != expected_ids:
        missing = sorted(expected_ids - supplied_ids)
        extra = sorted(supplied_ids - expected_ids)
        raise ReportingChecklistError(f"GATHER item mismatch; missing={missing}, extra={extra}")

    items: list[dict[str, Any]] = []
    for item_id, section, topic in GATHER_ITEMS:
        supplied = dict(evidence[item_id])
        status = supplied.get("status")
        if status not in {"satisfied", "partially_satisfied", "not_applicable", "planned"}:
            raise ReportingChecklistError(f"GATHER-{item_id:02d} has invalid status: {status}")
        evidence_paths = supplied.get("evidence", [])
        if not isinstance(evidence_paths, Sequence) or isinstance(evidence_paths, str):
            raise ReportingChecklistError(f"GATHER-{item_id:02d} evidence must be a list")
        rationale = supplied.get("rationale")
        if status != "satisfied" and not isinstance(rationale, str):
            raise ReportingChecklistError(
                f"GATHER-{item_id:02d} requires a rationale when not satisfied"
            )
        if status == "satisfied" and not evidence_paths:
            raise ReportingChecklistError(
                f"GATHER-{item_id:02d} cannot be satisfied without evidence"
            )
        item: dict[str, Any] = {
            "item_id": f"GATHER-{item_id:02d}",
            "number": item_id,
            "section": section,
            "topic": topic,
            "status": status,
            "evidence": sorted({str(path) for path in evidence_paths}),
        }
        if rationale is not None:
            item["rationale"] = str(rationale)
        items.append(item)

    counts = {
        status: sum(1 for item in items if item["status"] == status)
        for status in ("satisfied", "partially_satisfied", "not_applicable", "planned")
    }
    core = {
        "report_id": report_id,
        "title": title,
        "created_at": created_at,
        "standard": "GATHER",
        "standard_version": "2016-checklist-republished-2023",
        "source": GATHER_SOURCE,
        "scope_statement": scope_statement,
        "items": items,
        "summary": counts,
    }
    return {
        "schema_version": "1.0.0",
        "reporting_checklist_id": content_id("reporting", core),
        **core,
    }



def verify_gather_checklist(
    checklist: Mapping[str, Any], *, root: "Path | None" = None
) -> list[str]:
    """Recompute checklist identity, item coverage, counts and evidence-path safety.

    The verifier deliberately returns all detected failures so release assurance can show
    a complete audit trail rather than failing at the first malformed item.  Evidence paths
    must be relative regular files beneath ``root`` when a release root is supplied.
    """
    from pathlib import Path, PurePosixPath

    failures: list[str] = []
    expected = {number: (section, topic) for number, section, topic in GATHER_ITEMS}
    items = checklist.get("items")
    if not isinstance(items, list):
        return ["GATHER checklist items are unavailable"]

    seen: set[int] = set()
    calculated_counts = {
        status: 0
        for status in ("satisfied", "partially_satisfied", "not_applicable", "planned")
    }
    for index, raw in enumerate(items):
        if not isinstance(raw, Mapping):
            failures.append(f"GATHER item {index + 1} is not an object")
            continue
        number = raw.get("number")
        if not isinstance(number, int) or number not in expected:
            failures.append(f"GATHER item {index + 1} has invalid number: {number!r}")
            continue
        if number in seen:
            failures.append(f"GATHER-{number:02d} is duplicated")
        seen.add(number)
        section, topic = expected[number]
        if raw.get("item_id") != f"GATHER-{number:02d}":
            failures.append(f"GATHER-{number:02d} item_id is inconsistent")
        if raw.get("section") != section:
            failures.append(f"GATHER-{number:02d} section differs from the canonical checklist")
        if raw.get("topic") != topic:
            failures.append(f"GATHER-{number:02d} topic differs from the canonical checklist")
        status = raw.get("status")
        if status not in calculated_counts:
            failures.append(f"GATHER-{number:02d} has invalid status: {status!r}")
        else:
            calculated_counts[str(status)] += 1
        evidence = raw.get("evidence")
        if not isinstance(evidence, list) or any(not isinstance(item, str) for item in evidence):
            failures.append(f"GATHER-{number:02d} evidence is not a string list")
            continue
        if len(evidence) != len(set(evidence)):
            failures.append(f"GATHER-{number:02d} contains duplicate evidence paths")
        if status == "satisfied" and not evidence:
            failures.append(f"GATHER-{number:02d} is satisfied without evidence")
        if status != "satisfied" and not isinstance(raw.get("rationale"), str):
            failures.append(f"GATHER-{number:02d} lacks a rationale for status {status!r}")
        if root is not None:
            release_root = Path(root).resolve()
            for logical in evidence:
                pure = PurePosixPath(logical)
                if pure.is_absolute() or ".." in pure.parts or not pure.parts:
                    failures.append(f"GATHER-{number:02d} has unsafe evidence path: {logical}")
                    continue
                candidate = release_root.joinpath(*pure.parts)
                if candidate.is_symlink():
                    failures.append(f"GATHER-{number:02d} evidence is missing or unsafe: {logical}")
                    continue
                try:
                    candidate.resolve().relative_to(release_root)
                except ValueError:
                    failures.append(f"GATHER-{number:02d} evidence escapes the release: {logical}")
                    continue
                if logical.endswith("/"):
                    if not candidate.is_dir() or not any(candidate.iterdir()):
                        failures.append(
                            f"GATHER-{number:02d} evidence directory is missing or empty: {logical}"
                        )
                elif not candidate.is_file():
                    failures.append(f"GATHER-{number:02d} evidence is missing or unsafe: {logical}")

    missing = sorted(set(expected) - seen)
    if missing:
        failures.append("GATHER checklist is missing items: " + ", ".join(map(str, missing)))
    summary = checklist.get("summary")
    if summary != calculated_counts:
        failures.append("GATHER summary differs from recomputed item counts")

    core_keys = (
        "report_id",
        "title",
        "created_at",
        "standard",
        "standard_version",
        "source",
        "scope_statement",
        "items",
        "summary",
    )
    core = {key: checklist.get(key) for key in core_keys}
    expected_id = content_id("reporting", core)
    if checklist.get("reporting_checklist_id") != expected_id:
        failures.append("reporting_checklist_id differs from recomputed content identity")
    if checklist.get("standard") != "GATHER":
        failures.append("reporting checklist does not declare GATHER")
    if checklist.get("source") != GATHER_SOURCE:
        failures.append("reporting checklist source differs from the configured GATHER source")
    return sorted(set(failures))

def require_no_unresolved_reporting_items(checklist: Mapping[str, Any]) -> None:
    """Raise when planned or partially satisfied items remain."""
    items = checklist.get("items")
    if not isinstance(items, list):
        raise ReportingChecklistError("Checklist items are unavailable")
    unresolved = [
        item.get("item_id")
        for item in items
        if isinstance(item, Mapping)
        and item.get("status") in {"planned", "partially_satisfied"}
    ]
    if unresolved:
        raise ReportingChecklistError(
            "Unresolved reporting items: " + ", ".join(str(item) for item in unresolved)
        )


__all__ = [
    "GATHER_ITEMS",
    "GATHER_SOURCE",
    "ReportingChecklistError",
    "build_gather_checklist",
    "require_no_unresolved_reporting_items",
    "verify_gather_checklist",
]
