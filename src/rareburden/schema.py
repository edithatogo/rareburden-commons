"""Shared JSON/YAML loading and Draft 2020-12 validation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from yaml.nodes import MappingNode


class _StrictSafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _StrictSafeLoader, node: MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_StrictSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


class SchemaValidationError(ValueError):
    """Raised when a document is unreadable or fails its schema."""


# Backwards-compatible descriptive name used by newer modules.
DocumentValidationError = SchemaValidationError


def load_document(path: Path) -> Any:
    """Load JSON or YAML from *path* using safe parsing."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SchemaValidationError(f"Document not found: {path}") from exc

    try:
        if path.suffix.lower() == ".json":
            return json.loads(text)
        return yaml.load(text, Loader=_StrictSafeLoader)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise SchemaValidationError(f"Invalid document in {path}: {exc}") from exc


def load_mapping(path: Path) -> dict[str, Any]:
    """Load a JSON/YAML mapping, rejecting lists and scalar roots."""
    value = load_document(path)
    if not isinstance(value, dict):
        raise SchemaValidationError(f"Expected a mapping at the root of {path}")
    return value


def validate_instance(instance: Any, schema: dict[str, Any], *, label: str = "document") -> None:
    """Validate *instance* against a Draft 2020-12 JSON Schema."""
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(
        validator.iter_errors(instance), key=lambda item: tuple(str(part) for part in item.path)
    ):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{label}.{location}: {error.message}")
    if errors:
        formatted = "\n".join(f"- {message}" for message in errors)
        raise SchemaValidationError(f"Schema validation failed:\n{formatted}")


def validate_document(document: Any, schema: dict[str, Any], label: str = "document") -> None:
    """Compatibility wrapper around :func:`validate_instance`."""
    validate_instance(document, schema, label=label)


def validate_document_files(document_path: Path, schema_path: Path) -> Any:
    """Load and validate a JSON/YAML document, returning its parsed value."""
    document = load_document(document_path)
    validate_instance(document, load_mapping(schema_path), label=document_path.as_posix())
    return document
