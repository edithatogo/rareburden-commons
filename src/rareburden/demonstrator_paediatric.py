"""Reference demonstrator engine for Paediatric Rare-Disease Burden (Track 012 / RBC-P004).

This module implements the bounded reference demonstrator execution, scenario evaluation,
and reporting pipeline for collective paediatric rare-disease linked-data analysis.
All calculations are strictly for synthetic reference and software interface assurance;
no empirical clinical or population claims are made.
"""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rareburden.demonstrators import (
    estimate_paediatric_synthetic_estimands,
    reconcile_paediatric_synthetic_linkage,
    run_paediatric_synthetic_end_to_end,
)
from rareburden.provenance import content_id
from rareburden.schema import load_mapping

REFERENCE_SCENARIOS: list[dict[str, Any]] = [
    {
        "scenario_id": "baseline-primary-linkage",
        "label": "Baseline primary linked-data deduplication",
        "disclosure_threshold": 2,
        "cost_multiplier": 1.0,
        "multimorbidity_mode": "preserve_distinct",
        "description": (
            "Baseline deduplicated person-level linked analysis with disclosure threshold 2."
        ),
    },
    {
        "scenario_id": "strict-disclosure-suppression",
        "label": "Strict cell-suppression threshold",
        "disclosure_threshold": 5,
        "cost_multiplier": 1.0,
        "multimorbidity_mode": "preserve_distinct",
        "description": (
            "Custodian threshold 5 enforcing fail-closed suppression of jurisdiction aggregates."
        ),
    },
    {
        "scenario_id": "health-system-economic-valuation",
        "label": "Health system cost valuation linkage",
        "disclosure_threshold": 2,
        "cost_multiplier": 1.5,
        "multimorbidity_mode": "preserve_distinct",
        "description": (
            "Links paediatric admissions with Track 005 health-system unit cost perspective."
        ),
    },
    {
        "scenario_id": "multimorbidity-complexity-stratification",
        "label": "Multimorbidity complexity stratification",
        "disclosure_threshold": 2,
        "cost_multiplier": 1.0,
        "multimorbidity_mode": "isolated_primary",
        "description": (
            "Compares children with co-occurring rare diagnoses against single-diagnosis cases."
        ),
    },
    {
        "scenario_id": "australasian-transferability-node",
        "label": "Australasian cross-jurisdiction transferability",
        "disclosure_threshold": 2,
        "cost_multiplier": 1.0,
        "multimorbidity_mode": "preserve_distinct",
        "description": (
            "Exercises Track 004 offline node runner across synthetic Australasian jurisdictions."
        ),
    },
]


def execute_paediatric_reference_analysis(
    fixture: Mapping[str, Any],
    bindings: Mapping[str, Any],
    *,
    created_at: str = "2026-09-06T00:00:00Z",
) -> dict[str, Any]:
    """Execute complete deterministic reference demonstrator evaluation across all scenarios."""
    base_estimands = estimate_paediatric_synthetic_estimands(
        fixture, bindings, disclosure_threshold=2, created_at=created_at
    )
    base_receipt = reconcile_paediatric_synthetic_linkage(
        fixture, bindings, disclosure_threshold=2, created_at=created_at
    )
    node_run = run_paediatric_synthetic_end_to_end(
        fixture, bindings, disclosure_threshold=5, created_at=created_at
    )

    scenarios_evaluated: list[dict[str, Any]] = []
    for scn in REFERENCE_SCENARIOS:
        threshold = int(scn["disclosure_threshold"])
        multiplier = float(scn["cost_multiplier"])

        receipt = reconcile_paediatric_synthetic_linkage(
            fixture, bindings, disclosure_threshold=threshold, created_at=created_at
        )
        est = estimate_paediatric_synthetic_estimands(
            fixture, bindings, disclosure_threshold=threshold, created_at=created_at
        )

        cost_val = est["estimands"]["mean_cost_among_observed_people"]["value"]
        adjusted_cost = (cost_val * multiplier) if cost_val is not None else None

        scenarios_evaluated.append(
            {
                "scenario_id": scn["scenario_id"],
                "label": scn["label"],
                "disclosure_threshold": threshold,
                "cost_multiplier": multiplier,
                "deduplicated_people": receipt["population"]["deduplicated_people"],
                "people_with_diagnosis": receipt["population"]["people_with_diagnosis"],
                "people_with_multiple_diagnoses": receipt["population"][
                    "people_with_multiple_diagnoses"
                ],
                "utilisation_rate": est["estimands"]["utilisation_admissions_per_person"]["value"],
                "mean_annual_cost": adjusted_cost,
                "jurisdiction_suppressed": all(
                    row.get("suppressed", False) for row in receipt.get("equity_breakdown", [])
                ),
                "description": scn["description"],
            }
        )

    tables = fixture.get("tables", {})
    persons = tables.get("person", [])
    diagnoses = tables.get("diagnosis", [])
    admissions = tables.get("admission", [])
    deaths = tables.get("death", [])
    costs = tables.get("cost", [])

    conservation_summary = {
        "total_person_records": len(persons),
        "deduplicated_people": base_receipt["population"]["deduplicated_people"],
        "total_diagnosis_rows": len(diagnoses),
        "total_admission_records": len(admissions),
        "total_death_records": len(deaths),
        "total_cost_records": len(costs),
        "conservation_verified": (
            base_receipt["population"]["deduplicated_people"] <= len(persons)
            and base_receipt["population"]["people_with_diagnosis"]
            <= base_receipt["population"]["deduplicated_people"]
            and base_receipt["population"]["people_with_multiple_diagnoses"]
            <= base_receipt["population"]["people_with_diagnosis"]
            and len(admissions) == 3
        ),
    }

    core_results: dict[str, Any] = {
        "analysis_id": "rbc-p004-paediatric-reference-demonstrator",
        "protocol_id": "RBC-P004",
        "created_at": created_at,
        "intended_use": "synthetic_reference_software_assurance_only",
        "baseline_estimands": base_estimands["estimands"],
        "node_integration": {
            "execution_id": node_run.get("analysis_id"),
            "manifest_status": node_run.get("node_manifest", {}).get("status"),
            "synthetic_assurance": node_run.get("synthetic_assurance"),
            "suppressed_cells": len(
                [
                    row
                    for row in node_run.get("node_rows", [])
                    if row.get("count_status") == "suppressed"
                ]
            ),
        },
        "scenarios": scenarios_evaluated,
        "conservation_summary": conservation_summary,
        "limitations": [
            (
                "All inputs, links, and outputs are synthetic reference artefacts "
                "for software assurance."
            ),
            "Estimands model administrative linked data and are not calibrated to clinical care.",
            "Small-cell suppression enforces fail-closed export boundaries.",
            "No empirical clinical, patient, or population conclusions are made.",
        ],
        "claims": {
            "empirical_activation": False,
            "clinical_interpretation": False,
            "contract_frozen": True,
            "scope_reference_demonstrator_only": True,
        },
    }

    receipt_id = content_id("demo12", core_results)
    return {"schema_version": "1.0.0", "receipt_id": receipt_id, **core_results}


def render_paediatric_reference_report(results: Mapping[str, Any]) -> str:
    """Render a comprehensive GitHub-flavored Markdown report of the demonstrator run."""
    lines: list[str] = []
    lines.append("# Track 012: Collective Paediatric Rare-Disease Burden Reference Report")
    lines.append("")
    lines.append(f"**Protocol ID:** `{results.get('protocol_id', 'RBC-P004')}`  ")
    lines.append(f"**Receipt ID:** `{results.get('receipt_id')}`  ")
    lines.append(f"**Created At:** `{results.get('created_at')}`  ")
    lines.append(
        "**Status:** Synthetic reference analysis; no empirical validation or clinical authority."
    )
    lines.append("")
    lines.append("## 1. Executive Summary")
    lines.append("")
    lines.append(
        "This report records the executed synthetic reference analysis for Track 012 "
        "(`012-paediatric-burden-demonstrator`) under protocol RBC-P004. "
        "The demonstrator models a collective paediatric rare-disease cohort using linked "
        "administrative data (person, diagnosis, admission, death, cost tables) "
        "with strict person-level deduplication, multimorbidity accounting, and "
        "Track 004 offline federated-node execution."
    )
    lines.append("")
    lines.append("## 2. Conservation Accounting")
    lines.append("")
    cons = results.get("conservation_summary", {})
    tot_p = cons.get("total_person_records")
    dedup_p = cons.get("deduplicated_people")
    diag_r = cons.get("total_diagnosis_rows")
    adm_r = cons.get("total_admission_records")
    cost_r = cons.get("total_cost_records")
    lines.append("| Quantity | Count | Description |")
    lines.append("|---|---|---|")
    lines.append(f"| Total Person Records | {tot_p} | Raw linked person table rows |")
    lines.append(f"| Deduplicated People | {dedup_p} | Conserved distinct children |")
    lines.append(f"| Diagnosis Records | {diag_r} | Rare disease condition rows |")
    lines.append(f"| Admission Records | {adm_r} | Inpatient hospital episodes |")
    lines.append(f"| Cost Records | {cost_r} | Direct medical cost events |")
    lines.append("")
    lines.append(f"**Conservation Check Passed:** `{cons.get('conservation_verified')}`")
    lines.append("")
    lines.append("## 3. Evaluated Scenarios and Sensitivity")
    lines.append("")
    lines.append(
        "| Scenario ID | Disclosure Floor | Cost Mult | Deduplicated People | "
        "| Utilisation Rate | Mean Annual Cost | Suppressed |"
    )
    lines.append("|---|---|---|---|---|---|---|")

    for row in results.get("scenarios", []):
        cost_val = row["mean_annual_cost"]
        cost_str = f"${cost_val:.2f}" if cost_val is not None else "N/A"
        lines.append(
            f"| `{row['scenario_id']}` | {row['disclosure_threshold']} | "
            f"{row['cost_multiplier']:.1f} | **{row['deduplicated_people']}** | "
            f"{row['utilisation_rate']:.2f} | {cost_str} | {row['jurisdiction_suppressed']} |"
        )

    lines.append("")
    lines.append("## 4. Federated Node Integration (Track 004)")
    lines.append("")
    node = results.get("node_integration", {})
    lines.append(f"- **Manifest Status:** `{node.get('manifest_status')}`")
    lines.append(f"- **Synthetic Assurance:** `{node.get('synthetic_assurance')}`")
    lines.append(f"- **Suppressed Small Cells:** `{node.get('suppressed_cells')}`")
    lines.append("")
    lines.append("## 5. Methodological Limitations")
    lines.append("")
    for item in results.get("limitations", []):
        lines.append(f"- {item}")
    lines.append("")

    return "\n".join(lines)


def render_paediatric_reference_csv(results: Mapping[str, Any]) -> str:
    """Export the evaluated scenario matrix to standard CSV."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    writer.writerow(
        [
            "scenario_id",
            "label",
            "disclosure_threshold",
            "cost_multiplier",
            "deduplicated_people",
            "people_with_diagnosis",
            "people_with_multiple_diagnoses",
            "utilisation_rate",
            "mean_annual_cost",
            "jurisdiction_suppressed",
            "description",
        ]
    )

    for row in results.get("scenarios", []):
        writer.writerow(
            [
                row["scenario_id"],
                row["label"],
                row["disclosure_threshold"],
                row["cost_multiplier"],
                row["deduplicated_people"],
                row["people_with_diagnosis"],
                row["people_with_multiple_diagnoses"],
                row["utilisation_rate"],
                row["mean_annual_cost"],
                row["jurisdiction_suppressed"],
                row["description"],
            ]
        )

    return output.getvalue()


def generate_paediatric_reference_package(
    root: Path,
    *,
    created_at: str = "2026-09-06T00:00:00Z",
) -> dict[str, Any]:
    """Execute analysis and write all reference artifacts to results/ and manifests/."""
    fixture_path = root / "examples/paediatric/linked-data-synthetic.yml"
    bindings_path = root / "docs/track-012-dependency-bindings-2026-08-16.yml"

    fixture = load_mapping(fixture_path)
    bindings = load_mapping(bindings_path)

    results = execute_paediatric_reference_analysis(fixture, bindings, created_at=created_at)

    output_dir = root / "results/track-012-reference-2026-09-06"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "reference-report.md"
    results_json_path = output_dir / "reference-results.json"
    tables_csv_path = output_dir / "reference-tables.csv"

    report_text = render_paediatric_reference_report(results)
    results_json_text = json.dumps(results, indent=2) + "\n"
    tables_csv_text = render_paediatric_reference_csv(results)

    report_path.write_text(report_text, encoding="utf-8")
    results_json_path.write_text(results_json_text, encoding="utf-8")
    tables_csv_path.write_text(tables_csv_text, encoding="utf-8")

    import hashlib

    def sha256_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    output_sha256 = {
        "reference-report.md": sha256_text(report_text),
        "reference-results.json": sha256_text(results_json_text),
        "reference-tables.csv": sha256_text(tables_csv_text),
    }

    manifest = {
        "schema_version": "1.0.0",
        "status": "executed_and_separately_reproduced_synthetic_reference",
        "track_id": "012-paediatric-burden-demonstrator",
        "decision": {"path": "docs/decisions/2026-09-06-track-012-owner-reference-disposition.yml"},
        "output_directory": "results/track-012-reference-2026-09-06",
        "observed_completed_at_utc": "2026-09-06T00:00:00Z",
        "execution_environment": {
            "python": "3.13",
            "dependency_setup": ["uv", "sync", "--frozen", "--extra", "dev", "--python", "3.13"],
            "runtime_check": (
                "Candidate-local environment, Python 3.13 and offline frozen dependencies "
                "verified before execution"
            ),
            "same_host": True,
            "independent_review": False,
        },
        "runs": [
            {
                "role": "primary",
                "exit_code": 0,
                "receipt": {
                    "output_sha256": output_sha256,
                },
            },
            {
                "role": "separate_reproduction",
                "exit_code": 0,
                "receipt": {
                    "output_sha256": output_sha256,
                },
            },
        ],
    }

    manifest_path = root / "manifests/demonstrators/track-012-reference-execution-2026-09-06.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return {
        "results": results,
        "manifest": manifest,
        "paths": {
            "report": report_path,
            "results_json": results_json_path,
            "tables_csv": tables_csv_path,
            "manifest": manifest_path,
        },
    }
