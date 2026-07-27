#!/usr/bin/env python3
"""Validate the repository JSON Schema collection and identifier uniqueness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


def validate_schemas(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    identifiers: dict[str, Path] = {}
    for path in sorted(paths, key=lambda item: item.as_posix()):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: cannot read JSON Schema: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}: schema root must be an object")
            continue
        identifier = value.get("$id")
        if not isinstance(identifier, str):
            errors.append(f"{path}: $id is required")
        else:
            parsed = urlparse(identifier)
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"{path}: $id must be an absolute HTTPS URI")
            previous = identifiers.get(identifier)
            if previous is not None:
                errors.append(f"{path}: duplicate $id also used by {previous}: {identifier}")
            else:
                identifiers[identifier] = path
        if value.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{path}: $schema must declare Draft 2020-12")
        try:
            Draft202012Validator.check_schema(value)
        except SchemaError as exc:
            errors.append(f"{path}: invalid Draft 2020-12 schema: {exc.message}")
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--root", type=Path, default=Path("schemas"))
    args = parser.parse_args()
    paths = args.paths or sorted(args.root.glob("*.json"))
    errors = validate_schemas(paths)
    if errors:
        print("Schema validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Schemas passed: {len(paths)} schema(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
