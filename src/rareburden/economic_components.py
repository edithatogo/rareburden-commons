"""Validation-only support for the experimental synthetic component contract."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from copy import deepcopy
from importlib.resources import files
from typing import Any

from rareburden.schema import SchemaValidationError, validate_instance


class EconomicComponentError(ValueError):
    """Raised when an experimental component document is structurally invalid."""


def _check_structure(document: Mapping[str, Any]) -> None:
    """Reject cyclic or excessively large input before copying or validation."""
    stack: list[tuple[Any, int]] = [(document, 0)]
    seen: set[int] = set()
    nodes = 0
    while stack:
        value, depth = stack.pop()
        nodes += 1
        if nodes > 10_000 or depth > 20:
            raise EconomicComponentError("component prototype exceeds structure limits")
        if isinstance(value, (Mapping, list, tuple)):
            identity = id(value)
            if identity in seen:
                raise EconomicComponentError("component prototype exceeds structure limits")
            seen.add(identity)
            children = value.values() if isinstance(value, Mapping) else value
            stack.extend((child, depth + 1) for child in children)


def _canonical_schema() -> dict[str, Any]:
    try:
        resource = files("rareburden").joinpath(
            "resources", "repository", "schemas", "economic-component-prototype.schema.json"
        )
        value = json.loads(resource.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise EconomicComponentError("canonical component schema is unavailable") from None
    if not isinstance(value, dict):
        raise EconomicComponentError("canonical component schema is unavailable")
    return value


def validate_component_prototype(
    document: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate and detach synthetic component rows without calculating totals."""
    _check_structure(document)
    candidate = deepcopy(dict(document))
    try:
        validate_instance(candidate, _canonical_schema(), label="component prototype")
    except SchemaValidationError:
        raise EconomicComponentError("component prototype failed schema validation") from None

    component_ids: set[str] = set()
    for component in candidate["components"]:
        component_id = component["component_id"]
        if component_id in component_ids:
            raise EconomicComponentError("duplicate component identity")
        component_ids.add(component_id)
        value = component["quantity"].get("value")
        if value is not None and (
            isinstance(value, bool) or (not isinstance(value, int) and not math.isfinite(value))
        ):
            raise EconomicComponentError("component quantity must be a finite number")
        period = component["observation_period"]
        if period["end"] < period["start"]:
            raise EconomicComponentError("component observation period is reversed")
        monetary = component["quantity"]["kind"] == "monetary_shaped"
        statuses = component["valuation_readiness"]
        required_status = "unresolved" if monetary else "not_applicable"
        if any(
            statuses[field] != required_status
            for field in ("currency_status", "price_year_status", "valuation_status")
        ):
            raise EconomicComponentError("component valuation readiness is inconsistent")
        measurement = component["quantity"]["measurement_status"]
        missingness = component["missingness"]["status"]
        required_missingness = {
            "explicit_value": {"complete"},
            "explicit_zero": {"complete"},
            "not_collected": {"not_collected"},
            "unassessed": {"unassessed"},
            "not_applicable": {"not_applicable"},
            "missing": {"missing"},
        }.get(measurement)
        if required_missingness is not None and missingness not in required_missingness:
            raise EconomicComponentError("quantity and missingness status are inconsistent")

    for component in candidate["components"]:
        own_id = component["component_id"]
        overlap = component["overlap"]
        references = overlap["component_ids"]
        if own_id in references:
            raise EconomicComponentError("overlap assessment contains self-reference")
        if any(reference not in component_ids for reference in references):
            raise EconomicComponentError("overlap assessment contains unknown component")
        overlap_status = overlap["assessment_status"]
        if overlap_status in {"assessed_no_overlap", "unassessed", "not_applicable"} and references:
            raise EconomicComponentError("overlap status cannot list components")
        if overlap_status == "possible_overlap" and not references:
            raise EconomicComponentError("possible overlap requires a component reference")
    return candidate
