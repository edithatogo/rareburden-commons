"""Bounded synthetic summaries for the experimental economic component contract."""

from __future__ import annotations

import json
import math
from typing import Any

from rareburden.economic_components import validate_component_prototype
from rareburden.provenance import content_id


def calculate_synthetic_component_summary(document: dict[str, Any]) -> dict[str, Any]:
    """Summarise nonmonetary components without valuation or silent totals.

    Components are retained separately. Only explicit values assessed as having
    no overlap and sharing perspective, unit and denominator can form an
    aggregate. Missing, uncollected, possible-overlap and monetary-shaped rows
    remain visibly blocked.
    """
    candidate = validate_component_prototype(document)
    rows: list[dict[str, Any]] = []
    groups: dict[str, list[float]] = {}
    blocked: list[str] = []
    for component in candidate["components"]:
        quantity = component["quantity"]
        status = quantity["measurement_status"]
        component_id = component["component_id"]
        row = {
            "component_id": component_id,
            "perspective": component["perspective"]["label"],
            "kind": quantity["kind"],
            "unit": quantity["unit"],
            "measurement_status": status,
            "value": quantity.get("value"),
            "aggregation_status": "not_eligible",
        }
        if quantity["kind"] == "monetary_shaped":
            blocked.append(component_id)
        elif status in {"explicit_value", "explicit_zero"}:
            context = {
                "perspective": component["perspective"],
                "population": component["population"],
                "geography": component["geography"],
                "observation_period": component["observation_period"],
                "kind": quantity["kind"],
                "unit": quantity["unit"],
                "denominator_basis": quantity["denominator_basis"],
            }
            key = json.dumps(context, sort_keys=True, separators=(",", ":"))
            if component["overlap"]["assessment_status"] == "assessed_no_overlap":
                groups.setdefault(key, []).append(float(quantity["value"]))
                row["aggregation_status"] = "eligible"
            else:
                row["aggregation_status"] = "blocked_overlap_uncertainty"
        else:
            row["aggregation_status"] = "blocked_missingness"
        rows.append(row)
    aggregates = [
        {
            **json.loads(key),
            "value": math.fsum(values),
            "component_count": len(values),
        }
        for key, values in sorted(groups.items())
    ]
    core = {
        "schema_version": "0.1.0",
        "prototype_id": candidate["prototype_id"],
        "intended_use": "synthetic_assurance",
        "components": rows,
        "eligible_aggregates": aggregates,
        "valuation_blocked_component_ids": blocked,
        "limitations": [
            "All values are invented synthetic assurance inputs.",
            "Possible or unassessed overlap prevents aggregation.",
            "Monetary-shaped quantities are not valued, converted or totalled.",
        ],
    }
    return {"summary_id": content_id("econ", core), **core}


__all__ = ["calculate_synthetic_component_summary"]
