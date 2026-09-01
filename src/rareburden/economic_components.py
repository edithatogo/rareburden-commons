"""Validation-only support for the experimental synthetic component contract."""

from __future__ import annotations

import hashlib
import json
import math
from importlib.resources import files
from typing import Any

from rareburden.schema import SchemaValidationError, validate_instance


class EconomicComponentError(ValueError):
    """Raised when an experimental component document is structurally invalid."""


_CANONICAL_SCHEMA_SHA256 = "4176797d50c616ffa20fd44756adcf636ae134cfba2a45b41b076b956c1f3f53"
_MAX_STRUCTURE_NODES = 10_000
_MAX_STRUCTURE_DEPTH = 20


def _check_structure(document: dict[str, Any]) -> None:
    """Reject cyclic or excessively large input before copying or validation."""
    active: set[int] = set()
    nodes = 0

    def visit(value: Any, depth: int) -> None:
        nonlocal nodes
        nodes += 1
        if nodes > _MAX_STRUCTURE_NODES or depth > _MAX_STRUCTURE_DEPTH:
            raise EconomicComponentError("component prototype exceeds structure limits")
        if type(value) in {dict, list}:
            if len(value) > _MAX_STRUCTURE_NODES - nodes:
                raise EconomicComponentError("component prototype exceeds structure limits")
            identity = id(value)
            if identity in active:
                raise EconomicComponentError("component prototype exceeds structure limits")
            active.add(identity)
            if type(value) is dict:
                if any(type(key) is not str for key in value):
                    raise EconomicComponentError(
                        "component prototype contains unsupported structure"
                    )
                children = value.values()
            else:
                children = value
            try:
                for child in children:
                    visit(child, depth + 1)
            finally:
                active.remove(identity)
        elif type(value) not in {str, int, float, bool, type(None)}:
            raise EconomicComponentError("component prototype contains unsupported structure")

    visit(document, 0)


def _materialise_tree(value: Any) -> Any:
    """Detach every container occurrence without preserving shared aliases."""
    if type(value) is dict:
        return {key: _materialise_tree(item) for key, item in value.items()}
    if type(value) is list:
        return [_materialise_tree(item) for item in value]
    return value


def _canonical_schema() -> dict[str, Any]:
    try:
        resource = files("rareburden").joinpath(
            "resources", "repository", "schemas", "economic-component-prototype.schema.json"
        )
        text = resource.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise EconomicComponentError("canonical component schema is unavailable") from None
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != _CANONICAL_SCHEMA_SHA256:
        raise EconomicComponentError("canonical component schema is unavailable")
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        raise EconomicComponentError("canonical component schema is unavailable") from None
    if not isinstance(value, dict):
        raise EconomicComponentError("canonical component schema is unavailable")
    return value


def _is_finite_real_number(value: object) -> bool:
    """Accept native JSON numbers without coercing foreign numeric objects."""
    if type(value) is int:
        return True
    if type(value) is float:
        return math.isfinite(value)
    return False


def validate_component_prototype(
    document: dict[str, Any],
) -> dict[str, Any]:
    """Validate and detach synthetic component rows without calculating totals."""
    _check_structure(document)
    candidate = _materialise_tree(document)
    if not isinstance(candidate, dict):
        raise EconomicComponentError("component prototype failed schema validation")
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
        if value is not None and not _is_finite_real_number(value):
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
