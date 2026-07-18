"""Command-line entry point for RareBurden Commons utilities."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalog import CatalogValidationError, validate_catalog_files


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rareburden")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate-catalog", help="validate data-source metadata against its schema"
    )
    validate.add_argument(
        "--catalog",
        type=Path,
        default=Path("catalog/data_sources.yml"),
        help="path to the YAML catalogue",
    )
    validate.add_argument(
        "--schema",
        type=Path,
        default=Path("schemas/data-source.schema.json"),
        help="path to the JSON Schema",
    )
    validate.add_argument("--json", action="store_true", help="emit the summary as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "validate-catalog":
        try:
            summary = validate_catalog_files(args.catalog, args.schema)
        except CatalogValidationError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        payload = {
            "source_count": summary.source_count,
            "access_class_counts": summary.access_class_counts,
            "status_counts": summary.status_counts,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"Catalogue valid: {summary.source_count} sources")
            print(f"Access classes: {summary.access_class_counts}")
            print(f"Statuses: {summary.status_counts}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
