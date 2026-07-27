"""Versioned burden-purpose hierarchies, mappings and safe aggregation rules."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rareburden.provenance import content_id
from rareburden.schema import SchemaValidationError, load_mapping, validate_instance


class SemanticValidationError(ValueError):
    """Raised when a hierarchy, mapping or aggregation is semantically unsafe."""


@dataclass(frozen=True)
class DiseaseHierarchy:
    """Validated immutable hierarchy with burden-purpose aggregation contracts."""

    document: dict[str, Any]
    entities: dict[str, dict[str, Any]]
    aggregations: dict[str, dict[str, Any]]
    fingerprint: str

    def entity(self, entity_id: str) -> dict[str, Any]:
        """Return one entity or raise an actionable identifier error."""
        try:
            return self.entities[entity_id]
        except KeyError as exc:
            raise SemanticValidationError(f"Unknown entity_id: {entity_id}") from exc

    def aggregation(self, aggregation_id: str) -> dict[str, Any]:
        """Return one aggregation contract or raise an actionable identifier error."""
        try:
            return self.aggregations[aggregation_id]
        except KeyError as exc:
            raise SemanticValidationError(f"Unknown aggregation_id: {aggregation_id}") from exc

    def aggregate_counts(
        self,
        aggregation_id: str,
        counts: Mapping[str, float],
        *,
        unit: str = "people",
        require_complete: bool = True,
    ) -> dict[str, Any]:
        """Sum only an explicitly mutually-exclusive aggregation set.

        Non-exclusive and contextual hierarchies fail closed. Partial sums must be explicitly
        requested and remain labelled as partial rather than being presented as parent totals.
        """
        aggregation = self.aggregation(aggregation_id)
        if aggregation["strategy"] != "mutually_exclusive_sum":
            raise SemanticValidationError(
                f"{aggregation_id}: strategy {aggregation['strategy']!r} cannot be summed "
                "without an explicit overlap model"
            )
        if not unit.strip():
            raise SemanticValidationError("Aggregation unit must not be empty")

        members = tuple(str(value) for value in aggregation["member_entity_ids"])
        member_set = set(members)
        extras = sorted(set(counts) - member_set)
        if extras:
            raise SemanticValidationError(
                f"{aggregation_id}: counts contain non-member entities: {', '.join(extras)}"
            )
        missing = sorted(member_set - set(counts))
        if require_complete and missing:
            raise SemanticValidationError(
                f"{aggregation_id}: missing member counts: {', '.join(missing)}"
            )
        if not counts:
            raise SemanticValidationError(f"{aggregation_id}: no member counts supplied")

        inputs: list[dict[str, float | str]] = []
        for entity_id in members:
            if entity_id not in counts:
                continue
            value = counts[entity_id]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SemanticValidationError(f"{entity_id}: count must be numeric")
            numeric = float(value)
            if not math.isfinite(numeric) or numeric < 0:
                raise SemanticValidationError(f"{entity_id}: count must be finite and non-negative")
            inputs.append({"entity_id": entity_id, "value": numeric})

        coverage = "complete" if not missing else "partial"
        limitations = [
            "This result is valid only for the population, period, ascertainment and unit "
            "shared by all member inputs."
        ]
        if coverage == "partial":
            limitations.append(
                "The result is a labelled partial sum and must not be interpreted as the full "
                "parent-entity total."
            )
        elif not bool(aggregation["exhaustive"]):
            limitations.append(
                "The aggregation contract is not exhaustive; the sum may omit other parent "
                "aetiologies or residual cases."
            )

        core: dict[str, Any] = {
            "hierarchy_id": self.document["hierarchy_id"],
            "hierarchy_version": self.document["version"],
            "hierarchy_fingerprint": self.fingerprint,
            "aggregation_id": aggregation_id,
            "parent_entity_id": aggregation["parent_entity_id"],
            "strategy": aggregation["strategy"],
            "coverage": coverage,
            "unit": unit,
            "value": math.fsum(float(item["value"]) for item in inputs),
            "inputs": inputs,
            "missing_member_entity_ids": missing,
            "limitations": limitations,
        }
        return {"schema_version": "0.1.0", "result_id": content_id("sem", core), **core}


@dataclass(frozen=True)
class OntologyMappingSet:
    """Validated mapping set with a stable content fingerprint."""

    document: dict[str, Any]
    fingerprint: str


def _cycle_path(graph: Mapping[str, tuple[str, ...]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    path: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            start = path.index(node)
            return [*path[start:], node]
        if node in visited:
            return None
        visiting.add(node)
        path.append(node)
        for parent in graph[node]:
            cycle = visit(parent)
            if cycle is not None:
                return cycle
        path.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in sorted(graph):
        cycle = visit(node)
        if cycle is not None:
            return cycle
    return None


def validate_hierarchy(document: dict[str, Any], schema: dict[str, Any]) -> DiseaseHierarchy:
    """Validate schema plus graph, coding and aggregation invariants."""
    try:
        validate_instance(document, schema, label="disease_hierarchy")
    except SchemaValidationError as exc:
        raise SemanticValidationError(str(exc)) from exc

    errors: list[str] = []
    entities: dict[str, dict[str, Any]] = {}
    codes: dict[tuple[str, str, str], str] = {}
    for entity in document["entities"]:
        entity_id = str(entity["entity_id"])
        if entity_id in entities:
            errors.append(f"Duplicate entity_id: {entity_id}")
            continue
        entities[entity_id] = entity
        for code in entity["codes"]:
            key = (
                str(code["system"]).casefold(),
                str(code.get("version", "")),
                str(code["code"]),
            )
            existing = codes.get(key)
            if existing is not None:
                errors.append(
                    f"External code {code['system']}:{code['code']} is assigned to both "
                    f"{existing} and {entity_id}"
                )
            else:
                codes[key] = entity_id

    graph: dict[str, tuple[str, ...]] = {}
    parent_child_pairs: set[tuple[str, str]] = set()
    for entity_id, entity in entities.items():
        parents = tuple(str(parent) for parent in entity["parents"])
        graph[entity_id] = parents
        for parent in parents:
            if parent == entity_id:
                errors.append(f"{entity_id}: entity cannot be its own parent")
            elif parent not in entities:
                errors.append(f"{entity_id}: unknown parent entity {parent}")
            else:
                parent_child_pairs.add((parent, entity_id))
    if not errors:
        cycle = _cycle_path(graph)
        if cycle is not None:
            errors.append("Hierarchy cycle detected: " + " -> ".join(cycle))

    aggregations: dict[str, dict[str, Any]] = {}
    parent_aggregations: dict[str, str] = {}
    represented_pairs: set[tuple[str, str]] = set()
    for aggregation in document["aggregation_sets"]:
        aggregation_id = str(aggregation["aggregation_id"])
        if aggregation_id in aggregations:
            errors.append(f"Duplicate aggregation_id: {aggregation_id}")
            continue
        aggregations[aggregation_id] = aggregation
        parent = str(aggregation["parent_entity_id"])
        previous = parent_aggregations.get(parent)
        if previous is not None:
            errors.append(
                f"Parent {parent} has multiple aggregation sets: {previous}, {aggregation_id}"
            )
        else:
            parent_aggregations[parent] = aggregation_id
        if parent not in entities:
            errors.append(f"{aggregation_id}: unknown parent entity {parent}")
            continue
        if entities[parent]["aggregation_role"] == "leaf":
            errors.append(f"{aggregation_id}: parent {parent} is declared as a leaf")
        members = tuple(str(value) for value in aggregation["member_entity_ids"])
        if parent in members:
            errors.append(f"{aggregation_id}: parent cannot also be a member")
        for member in members:
            if member not in entities:
                errors.append(f"{aggregation_id}: unknown member entity {member}")
                continue
            represented_pairs.add((parent, member))
            if parent not in entities[member]["parents"]:
                errors.append(
                    f"{aggregation_id}: member {member} does not declare {parent} as a parent"
                )
        unclassified = aggregation.get("unclassified_member_id")
        if unclassified is not None and unclassified not in members:
            errors.append(
                f"{aggregation_id}: unclassified_member_id must be one of member_entity_ids"
            )
        if bool(aggregation["exhaustive"]) and not unclassified:
            errors.append(
                f"{aggregation_id}: exhaustive aggregation requires an explicit "
                "unclassified_member_id"
            )

    missing_contracts = sorted(parent_child_pairs - represented_pairs)
    for parent, child in missing_contracts:
        errors.append(f"Parent-child relation {parent} -> {child} lacks an aggregation contract")
    extra_contracts = sorted(represented_pairs - parent_child_pairs)
    for parent, child in extra_contracts:
        errors.append(f"Aggregation relation {parent} -> {child} is absent from entity parents")

    children = {parent for parent, _ in parent_child_pairs}
    for entity_id in sorted(children):
        if entities[entity_id]["aggregation_role"] == "leaf":
            errors.append(f"{entity_id}: entity has children but is declared as a leaf")
    for entity_id, entity in entities.items():
        if entity["aggregation_role"] != "leaf" and entity_id not in children:
            errors.append(f"{entity_id}: non-leaf entity has no children")

    if errors:
        raise SemanticValidationError(
            "Disease hierarchy validation failed:\n- " + "\n- ".join(errors)
        )
    fingerprint = content_id("hier", document)
    return DiseaseHierarchy(
        document=document,
        entities=entities,
        aggregations=aggregations,
        fingerprint=fingerprint,
    )


def load_hierarchy(document_path: Path, schema_path: Path) -> DiseaseHierarchy:
    """Load and validate a disease hierarchy from YAML or JSON."""
    return validate_hierarchy(load_mapping(document_path), load_mapping(schema_path))


def validate_mapping_set(document: dict[str, Any], schema: dict[str, Any]) -> OntologyMappingSet:
    """Validate mapping-schema and ambiguity invariants."""
    try:
        validate_instance(document, schema, label="ontology_mapping")
    except SchemaValidationError as exc:
        raise SemanticValidationError(str(exc)) from exc

    errors: list[str] = []
    seen: set[tuple[str, str | None, str]] = set()
    accepted_exact: dict[str, str] = {}
    for mapping in document["mappings"]:
        source = str(mapping["source_code"])
        target_value = mapping.get("target_code")
        target = str(target_value) if target_value is not None else None
        relation = str(mapping["relation"])
        key = (source, target, relation)
        if key in seen:
            errors.append(f"Duplicate mapping: {source} {relation} {target or '<none>'}")
        seen.add(key)
        if relation == "unmapped" and target is not None:
            errors.append(f"{source}: unmapped relation cannot have a target_code")
        if relation != "unmapped" and target is None:
            errors.append(f"{source}: {relation} relation requires a target_code")
        if (
            mapping["status"] == "accepted"
            and relation == "exact"
            and mapping["confidence"] in {"low", "unclear"}
        ):
            errors.append(f"{source}: accepted exact mapping requires moderate or high confidence")
        if mapping["status"] == "accepted" and relation == "exact" and target is not None:
            previous = accepted_exact.get(source)
            if previous is not None and previous != target:
                errors.append(
                    f"{source}: accepted exact mappings are ambiguous between "
                    f"{previous} and {target}"
                )
            else:
                accepted_exact[source] = target
    if errors:
        raise SemanticValidationError(
            "Ontology mapping validation failed:\n- " + "\n- ".join(errors)
        )
    return OntologyMappingSet(document=document, fingerprint=content_id("map", document))


def load_mapping_set(document_path: Path, schema_path: Path) -> OntologyMappingSet:
    """Load and validate an ontology mapping set from YAML or JSON."""
    return validate_mapping_set(load_mapping(document_path), load_mapping(schema_path))


__all__ = [
    "DiseaseHierarchy",
    "OntologyMappingSet",
    "SemanticValidationError",
    "load_hierarchy",
    "load_mapping_set",
    "validate_hierarchy",
    "validate_mapping_set",
]
