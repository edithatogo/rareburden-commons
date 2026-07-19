"""Command-line entry point for RareBurden Commons utilities."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalog import CatalogValidationError, validate_catalog_files
from .roadmap import RoadmapValidationError, validate_roadmap_files


def _add_catalog_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path("catalog/data_sources.yml"),
        help="path to the YAML source catalogue",
    )
    parser.add_argument(
        "--catalog-schema",
        "--schema",
        dest="catalog_schema",
        type=Path,
        default=Path("schemas/data-source.schema.json"),
        help="path to the data-source JSON Schema",
    )


def _add_roadmap_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--roadmap",
        type=Path,
        default=Path("conductor/roadmap.yml"),
        help="path to the machine-readable release roadmap",
    )
    parser.add_argument(
        "--roadmap-schema",
        type=Path,
        default=Path("schemas/roadmap.schema.json"),
        help="path to the roadmap JSON Schema",
    )
    parser.add_argument(
        "--tracks-root",
        type=Path,
        default=Path("conductor/tracks"),
        help="directory containing Conductor tracks",
    )
    parser.add_argument(
        "--track-schema",
        type=Path,
        default=Path("schemas/track-metadata.schema.json"),
        help="path to the track metadata JSON Schema",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rareburden")
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog = subparsers.add_parser(
        "validate-catalog", help="validate data-source metadata against its schema"
    )
    _add_catalog_arguments(catalog)
    catalog.add_argument("--json", action="store_true", help="emit the summary as JSON")

    roadmap = subparsers.add_parser(
        "validate-roadmap", help="validate the release roadmap and Conductor track graph"
    )
    _add_roadmap_arguments(roadmap)
    roadmap.add_argument("--json", action="store_true", help="emit the summary as JSON")

    programme = subparsers.add_parser(
        "validate-programme", help="validate catalogue, roadmap and track controls together"
    )
    _add_catalog_arguments(programme)
    _add_roadmap_arguments(programme)
    programme.add_argument("--json", action="store_true", help="emit the summary as JSON")
    return parser


def _catalog_payload(args: argparse.Namespace) -> dict[str, object]:
    summary = validate_catalog_files(args.catalog, args.catalog_schema)
    return {
        "source_count": summary.source_count,
        "access_class_counts": summary.access_class_counts,
        "status_counts": summary.status_counts,
    }


def _roadmap_payload(args: argparse.Namespace) -> dict[str, object]:
    summary = validate_roadmap_files(
        args.roadmap,
        args.roadmap_schema,
        args.tracks_root,
        args.track_schema,
    )
    return {
        "release_count": summary.release_count,
        "track_count": summary.track_count,
        "v1_critical_track_count": summary.v1_critical_track_count,
        "current_release": summary.current_release,
        "track_status_counts": summary.track_status_counts,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    try:
        if args.command == "validate-catalog":
            payload: dict[str, object] = _catalog_payload(args)
        elif args.command == "validate-roadmap":
            payload = _roadmap_payload(args)
        elif args.command == "validate-programme":
            payload = {
                "catalog": _catalog_payload(args),
                "roadmap": _roadmap_payload(args),
            }
        else:
            return 2
    except (CatalogValidationError, RoadmapValidationError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif args.command == "validate-catalog":
        print(f"Catalogue valid: {payload['source_count']} sources")
        print(f"Access classes: {payload['access_class_counts']}")
        print(f"Statuses: {payload['status_counts']}")
    elif args.command == "validate-roadmap":
        print(
            "Roadmap valid: "
            f"{payload['track_count']} tracks across {payload['release_count']} releases"
        )
        print(f"Current release: {payload['current_release']}")
        print(f"Track statuses: {payload['track_status_counts']}")
    else:
        catalog = payload["catalog"]
        roadmap = payload["roadmap"]
        assert isinstance(catalog, dict)
        assert isinstance(roadmap, dict)
        print(
            "Programme valid: "
            f"{catalog['source_count']} sources, "
            f"{roadmap['track_count']} tracks, "
            f"{roadmap['release_count']} releases"
        )
        print(f"Current release: {roadmap['current_release']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
