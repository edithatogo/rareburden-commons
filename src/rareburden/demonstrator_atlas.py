"""Reference demonstrator engine for Atlas, API and Release Engineering (Track 014).

This module implements the bounded release candidate packaging, static projection,
read-only API shape, accessibility consistency verification, and reference reporting.
"""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rareburden.atlas import (
    build_atlas_release_candidate,
    build_atlas_release_status,
    build_gap_api_response,
    build_gap_package,
    build_static_product_set,
    validate_accessibility_consistency,
)
from rareburden.gapmap import build_domain_gap_map
from rareburden.provenance import content_id
from rareburden.schema import load_mapping


def execute_atlas_reference_analysis(root: Path) -> dict[str, Any]:
    """Execute the full Track 014 reference atlas release packaging pipeline."""
    catalog_path = root / "catalog/data_sources.yml"
    needs_path = root / "examples/config/gap-map-needs.yml"

    catalog = load_mapping(catalog_path)
    needs = load_mapping(needs_path)

    gap_map = build_domain_gap_map(catalog, needs)
    package = build_gap_package(
        gap_map,
        release_id="track-014-reference-v0.8-beta",
        source_manifest_id="track-013-demonstrator-validation-2026-09-06",
    )
    api_response = build_gap_api_response(package)

    reviewed_artifacts: list[Mapping[str, Any]] = [
        {
            "artifact_id": "track-013-demonstrator-validation",
            "sha256": "1801244977de245cea84551cd3fbe00c71f3bce5c6fd58d1a5bcbd9784afc36a",
            "package_fingerprint": package["package_fingerprint"],
            "review_receipt_id": "track-013-reference-output-panel-2026-09-06",
            "review_state": "repository_reviewed_bounded",
            "licence_state": "metadata_only",
        }
    ]

    candidate = build_atlas_release_candidate(
        package,
        api_response,
        reviewed_artifacts=reviewed_artifacts,
        citation_id="citation-track-014-reference",
        provenance_id="prov-track-014-reference",
    )

    status = build_atlas_release_status(candidate, [])
    product_set = build_static_product_set(
        package,
        candidate,
        status,
        country_scope_id="XAA",
        demonstrator_scope_id="synthetic-public-foundation",
    )

    consistency = validate_accessibility_consistency(package, api_response, product_set)

    core = {
        "schema_version": "1.0.0",
        "release_id": package["release_id"],
        "protocol_id": "RBC-R001",
        "pipeline_version": "0.3.0rc2",
        "created_at": "2026-09-06T00:00:00Z",
        "intended_use": "synthetic_assurance",
        "package_fingerprint": package["package_fingerprint"],
        "release_surface_fingerprint": candidate["release_surface_fingerprint"],
        "status_fingerprint": status["status_fingerprint"],
        "product_set_fingerprint": product_set["product_set_fingerprint"],
        "consistency_validation": consistency,
        "product_count": len(product_set["products"]),
        "api_row_count": len(api_response["rows"]),
        "gap_map_summary": {
            "total_domains": len(gap_map.get("rows", [])),
            "missingness_policy": package["missingness_policy"],
        },
        "limitations": [
            "All atlas projections are synthetic reference artefacts for software assurance.",
            "Static and API projections use user-assigned country codes (XAA-XZZ) only.",
            "No hosted network API or public website is activated by this release candidate.",
            "Release claims enforce fail-closed boundaries under ADR-0005 and ADR-0009.",
        ],
        "claims": {
            "synthetic_projection_executable": True,
            "real_source_activation": False,
            "accessibility_approved": False,
            "independent_reproduction": False,
            "release_authority_approval": False,
            "public_release": False,
            "stable_release": False,
        },
    }
    return {"receipt_id": content_id("t014atlas", core), **core}


def render_track014_reference_report(results: Mapping[str, Any]) -> str:
    """Render the Track 014 atlas reference report in Markdown."""
    lines: list[str] = [
        "# Track 014: Atlas, API and Reproducible Release Reference Report",
        "",
        f"**Protocol ID:** `{results.get('protocol_id')}`  ",
        f"**Release ID:** `{results.get('release_id')}`  ",
        f"**Receipt ID:** `{results.get('receipt_id')}`  ",
        f"**Created At:** `{results.get('created_at')}`  ",
        f"**Intended Use:** `{results.get('intended_use')}`  ",
        "",
        "## 1. Executive Summary and Governance Boundary",
        "",
        "This report records the bounded release engineering candidate for Track 014.",
        "The release projects reviewed aggregate evidence from Tracks 008 through 013",
        "into static products, aggregate data packages, and read-only API shapes.",
        "All products are strictly synthetic and non-published under ADR-0005 and ADR-0009.",
        "",
        "## 2. Release Surface Fingerprints",
        "",
        f"- **Package Fingerprint:** `{results.get('package_fingerprint')}`",
        f"- **Release Surface Fingerprint:** `{results.get('release_surface_fingerprint')}`",
        f"- **Status Fingerprint:** `{results.get('status_fingerprint')}`",
        f"- **Product Set Fingerprint:** `{results.get('product_set_fingerprint')}`",
        "",
        "## 3. Product and Consistency Verification",
        "",
        f"- **Products Generated:** `{results.get('product_count')}`",
        f"- **API Rows Emitted:** `{results.get('api_row_count')}`",
    ]
    cons = results.get("consistency_validation", {})
    lines.append(f"- **Consistency Status:** `{cons.get('status')}`")
    lines.append(f"- **Human Conformance Assessed:** `{cons.get('human_conformance_assessed')}`")
    lines.append(f"- **Real User Testing Observed:** `{cons.get('real_user_testing_observed')}`")
    lines.append("")

    lines.append("## 4. Declared Limitations")
    lines.append("")
    for lim in results.get("limitations", []):
        lines.append(f"- {lim}")
    lines.append("")

    return "\n".join(lines)


def render_track014_reference_csv(results: Mapping[str, Any]) -> str:
    """Render the Track 014 reference summary table as CSV."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["component", "identifier", "metric", "value", "state"])

    writer.writerow(
        [
            "surface",
            "package",
            "fingerprint",
            results.get("package_fingerprint"),
            "bound",
        ]
    )
    writer.writerow(
        [
            "surface",
            "release_candidate",
            "fingerprint",
            results.get("release_surface_fingerprint"),
            "prepared",
        ]
    )
    writer.writerow(
        [
            "surface",
            "status",
            "fingerprint",
            results.get("status_fingerprint"),
            "active",
        ]
    )
    writer.writerow(
        [
            "surface",
            "product_set",
            "fingerprint",
            results.get("product_set_fingerprint"),
            "verified",
        ]
    )
    writer.writerow(
        [
            "consistency",
            "accessibility_contract",
            "product_count",
            results.get("product_count"),
            "consistent",
        ]
    )

    return output.getvalue()


def generate_track014_reference_package(root: Path) -> dict[str, Any]:
    """Execute analysis and write deterministic reference package to disk."""
    results = execute_atlas_reference_analysis(root)
    out_dir = root / "results/track-014-reference-2026-09-06"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "reference-results.json"
    report_path = out_dir / "reference-report.md"
    csv_path = out_dir / "reference-tables.csv"

    json_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_track014_reference_report(results) + "\n", encoding="utf-8")
    csv_path.write_text(render_track014_reference_csv(results), encoding="utf-8")

    return {
        "receipt_id": results["receipt_id"],
        "paths": {
            "results_json": json_path,
            "report_md": report_path,
            "tables_csv": csv_path,
        },
        "results": results,
    }
