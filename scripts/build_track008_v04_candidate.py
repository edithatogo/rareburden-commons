#!/usr/bin/env python3
"""Build the bounded Track 008 v0.4 mapping and provisional naming candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

ORPHADATA_SHA256 = "df8d562a0c6011af36a74eb4000ce81ca7d723e8031010819fb71727c0962bbb"
MONDO_SHA256 = "7cf8f1df31185555a21f5ffaf36663ca420671a9bc234fc737eb9bfa977ecd60"
HPO_SHA256 = "3b646565695329aa399e937883c68d5d424d0df5eaab2f22baa0e08d44fdbe87"
MONDO_PREFIX = "http://purl.obolibrary.org/obo/MONDO_"
HPO_PREFIX = "http://purl.obolibrary.org/obo/HP_"
ORPHA_EXACT = re.compile(r"Orphanet_(\d+)$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_digest(path: Path, expected: str) -> None:
    observed = _sha256(path)
    if observed != expected:
        raise ValueError(f"source digest mismatch for {path}: {observed} != {expected}")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _orpha_labels(path: Path) -> dict[str, str]:
    root = ElementTree.parse(path).getroot()
    labels: dict[str, str] = {}
    for disorder in root.findall(".//Disorder"):
        code = disorder.findtext("OrphaCode")
        label = disorder.findtext("Name")
        if code and label:
            if code in labels:
                raise ValueError(f"duplicate OrphaCode in exact source: {code}")
            labels[code] = label
    return labels


def _mondo_exact_rows(document: dict[str, Any]) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for graph in document.get("graphs", []):
        for node in graph.get("nodes", []):
            node_id = str(node.get("id", ""))
            if not node_id.startswith(MONDO_PREFIX) or not node.get("lbl"):
                continue
            mondo_code = f"MONDO:{node_id.removeprefix(MONDO_PREFIX)}"
            for value in node.get("meta", {}).get("basicPropertyValues", []):
                if value.get("pred") != "http://www.w3.org/2004/02/skos/core#exactMatch":
                    continue
                match = ORPHA_EXACT.search(str(value.get("val", "")))
                if match:
                    rows.append((match.group(1), mondo_code, str(node["lbl"])))
    rows.sort(key=lambda row: (int(row[0]), row[1]))
    return rows


def _hpo_labels(document: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for graph in document.get("graphs", []):
        for node in graph.get("nodes", []):
            node_id = str(node.get("id", ""))
            label = node.get("lbl")
            if node_id.startswith(HPO_PREFIX) and isinstance(label, str) and label:
                rows.append(
                    {
                        "code": f"HP:{node_id.removeprefix(HPO_PREFIX)}",
                        "source_label": label,
                        "provisional_display_label": label,
                        "authority": "source_native_not_community_approved",
                    }
                )
    return sorted(rows, key=lambda row: row["code"])


def build(
    orphadata: Path, mondo: Path, hpo: Path
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    _require_digest(orphadata, ORPHADATA_SHA256)
    _require_digest(mondo, MONDO_SHA256)
    _require_digest(hpo, HPO_SHA256)
    orpha_labels = _orpha_labels(orphadata)
    mondo_rows = _mondo_exact_rows(_load_json(mondo))
    target_counts = Counter(source for source, _, _ in mondo_rows)
    ambiguous = sorted(source for source, count in target_counts.items() if count > 1)
    if ambiguous:
        raise ValueError(f"ambiguous ORPHA-to-MONDO targets require review: {ambiguous[:10]}")
    included = [row for row in mondo_rows if row[0] in orpha_labels]
    excluded = [row for row in mondo_rows if row[0] not in orpha_labels]

    mappings = [
        {
            "source_code": f"ORPHA:{orpha}",
            "target_code": mondo_code,
            "relation": "exact",
            "confidence": "moderate",
            "status": "provisional",
            "rationale": (
                "MONDO v2026-08-04 asserts skos:exactMatch to this Orphanet code, "
                "which is present in the exact Orphadata July 2026 alignment release."
            ),
            "evidence_refs": [
                f"sha256:{ORPHADATA_SHA256}",
                f"sha256:{MONDO_SHA256}",
            ],
        }
        for orpha, mondo_code, _ in included
    ]
    mapping = {
        "schema_version": "0.1.0",
        "mapping_set_id": "orpha-2026-07-to-mondo-2026-08-04",
        "title": "Provisional non-clinical ORPHA-to-MONDO exact-match candidate",
        "version": "0.4.0",
        "source_system": "ORPHA",
        "source_version": "Orphanet knowledge base release of July 2026",
        "target_system": "MONDO",
        "target_version": "v2026-08-04",
        "mappings": mappings,
        "limitations": [
            "Every row is provisional and intended only for non-clinical identifier alignment.",
            "Exact denotes the MONDO source assertion, not independent clinical equivalence.",
            "The intersection is bounded to two exact releases and is not comprehensive coverage.",
            "No mapping is accepted for diagnostic, treatment or patient-level decision support.",
        ],
    }
    naming = {
        "schema_version": "1.0.0",
        "track": "008-semantic-backbone",
        "status": "provisional_owner_operated_not_community_approved",
        "mapping_labels": [
            {
                "source_code": f"ORPHA:{orpha}",
                "source_label": orpha_labels[orpha],
                "target_code": mondo_code,
                "target_label": mondo_label,
                "provisional_display_label": orpha_labels[orpha],
                "authority": "source_native_not_clinically_or_community_approved",
            }
            for orpha, mondo_code, mondo_label in included
        ],
        "hpo_labels": _hpo_labels(_load_json(hpo)),
        "groupings_added": [],
        "rules": [
            "Preserve source-native labels and identifiers.",
            "Do not silently harmonise label differences.",
            "Use aliases and versioned deprecation for later changes.",
            "Do not imply clinical or patient-community authority.",
        ],
    }
    receipt = {
        "schema_version": "1.0.0",
        "track": "008-semantic-backbone",
        "status": "candidate_rows_generated_not_frozen",
        "source_hashes": {
            "orphadata": ORPHADATA_SHA256,
            "mondo": MONDO_SHA256,
            "hpo": HPO_SHA256,
        },
        "counts": {
            "orphadata_codes": len(orpha_labels),
            "mondo_orphanet_exact_assertions": len(mondo_rows),
            "included_intersection_rows": len(included),
            "excluded_absent_from_exact_orphadata": len(excluded),
            "ambiguous_orpha_codes": len(ambiguous),
            "hpo_source_native_labels": len(naming["hpo_labels"]),
            "new_owner_defined_groupings": 0,
        },
        "excluded_rows": [
            {"source_code": f"ORPHA:{orpha}", "target_code": mondo_code, "target_label": label}
            for orpha, mondo_code, label in excluded
        ],
        "interpretation": (
            "Rows are the exact-release intersection of MONDO skos:exactMatch assertions and "
            "Orphadata codes. Generation does not constitute clinical validation, independent "
            "review, community approval, contract freeze or Track 008 completion."
        ),
    }
    return mapping, naming, receipt


def _write(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orphadata", type=Path, required=True)
    parser.add_argument("--mondo", type=Path, required=True)
    parser.add_argument("--hpo", type=Path, required=True)
    parser.add_argument("--mapping-output", type=Path, required=True)
    parser.add_argument("--naming-output", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path, required=True)
    args = parser.parse_args()
    mapping, naming, receipt = build(args.orphadata, args.mondo, args.hpo)
    _write(args.mapping_output, mapping)
    _write(args.naming_output, naming)
    _write(args.receipt_output, receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
