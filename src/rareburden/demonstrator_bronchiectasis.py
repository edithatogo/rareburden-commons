"""Reference demonstrator engine for Bronchiectasis rare-aetiology analysis (Track 011 / RBC-P003).

This module implements the bounded reference demonstrator execution, scenario evaluation,
and reporting pipeline for bronchiectasis rare-within-common analysis.
All calculations are strictly for synthetic reference and software interface assurance;
no empirical clinical or population claims are made.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rareburden.demonstrators import (
    reconcile_bronchiectasis_synthetic_profile,
    run_bronchiectasis_synthetic_scenarios,
)
from rareburden.provenance import content_id
from rareburden.schema import load_mapping
from rareburden.semantics import DiseaseHierarchy, load_hierarchy

REFERENCE_SCENARIOS: list[dict[str, Any]] = [
    {
        "scenario_id": "baseline-primary-exclusive",
        "label": "Baseline primary exclusive classification",
        "hierarchy_mode": "primary",
        "multi_aetiology_fraction": 0.0,
        "unknown_fraction": 0.0,
        "transport_multiplier": 1.0,
        "exacerbation_rate": 0.8,
        "treatment_eligibility_fraction": 0.80,
        "description": (
            "Strict mutually exclusive classification without multi-aetiology attribution."
        ),
    },
    {
        "scenario_id": "proportional-overlap",
        "label": "Proportional multi-aetiology overlap",
        "hierarchy_mode": "primary",
        "multi_aetiology_fraction": 0.25,
        "unknown_fraction": 0.10,
        "transport_multiplier": 1.0,
        "exacerbation_rate": 0.9,
        "treatment_eligibility_fraction": 0.82,
        "description": (
            "Proportional attribution: 25% of multi-aetiology and 10% of unclassified cases "
            "contain primary aetiology."
        ),
    },
    {
        "scenario_id": "high-overlap-multimorbidity",
        "label": "High overlap and complex multimorbidity",
        "hierarchy_mode": "primary",
        "multi_aetiology_fraction": 0.50,
        "unknown_fraction": 0.20,
        "transport_multiplier": 1.0,
        "exacerbation_rate": 1.2,
        "treatment_eligibility_fraction": 0.85,
        "description": (
            "High-overlap sensitivity: half of multi-aetiology and 20% of unknown cases "
            "involve primary cause."
        ),
    },
    {
        "scenario_id": "tertiary-referral-transport",
        "label": "Tertiary referral centre transport scenario",
        "hierarchy_mode": "primary",
        "multi_aetiology_fraction": 0.35,
        "unknown_fraction": 0.15,
        "transport_multiplier": 1.35,
        "exacerbation_rate": 1.5,
        "treatment_eligibility_fraction": 0.90,
        "description": (
            "Tertiary referral setting: referral enrichment multiplier (1.35x) "
            "reflecting tertiary clinic selection."
        ),
    },
    {
        "scenario_id": "community-ascertainment-transport",
        "label": "Unselected community cohort transport scenario",
        "hierarchy_mode": "primary",
        "multi_aetiology_fraction": 0.15,
        "unknown_fraction": 0.05,
        "transport_multiplier": 0.75,
        "exacerbation_rate": 0.6,
        "treatment_eligibility_fraction": 0.70,
        "description": (
            "Community setting: lower specialized ascertainment multiplier (0.75x) "
            "in primary care cohorts."
        ),
    },
    {
        "scenario_id": "restricted-diagnostic-capacity",
        "label": "Restricted diagnostic capacity scenario",
        "hierarchy_mode": "primary",
        "multi_aetiology_fraction": 0.10,
        "unknown_fraction": 0.02,
        "transport_multiplier": 0.60,
        "exacerbation_rate": 0.7,
        "treatment_eligibility_fraction": 0.65,
        "description": (
            "Restricted capacity: limited access to sweat chloride, ciliary biopsy "
            "or gene panels (0.60x)."
        ),
    },
]


def load_bronchiectasis_reference_inputs(
    root: Path | None = None,
) -> dict[str, Any]:
    """Load and validate all reference fixtures and dependency bindings for Track 011."""
    if root is None:
        root = Path(__file__).resolve().parents[2]

    profile_path = root / "examples/demonstrators/011-bounded-synthetic-profile.yml"
    hierarchy_path = root / "examples/semantics/bronchiectasis-synthetic.yml"
    schema_path = root / "schemas/disease-hierarchy.schema.json"
    bindings_path = root / "docs/track-011-dependency-bindings-2026-08-16.yml"

    profile = load_mapping(profile_path)
    hierarchy = load_hierarchy(hierarchy_path, schema_path)
    bindings = load_mapping(bindings_path)

    return {
        "profile": profile,
        "hierarchy": hierarchy,
        "bindings": bindings,
        "scenarios": REFERENCE_SCENARIOS,
    }


def execute_bronchiectasis_reference_pipeline(
    inputs: Mapping[str, Any],
    *,
    created_at: str = "2026-09-05T00:00:00Z",
) -> dict[str, Any]:
    """Execute the full bounded synthetic bronchiectasis demonstrator pipeline.

    Produces deterministic scenario evaluations, conservation accounting,
    and reference ranges.
    """
    profile = inputs["profile"]
    hierarchy: DiseaseHierarchy = inputs["hierarchy"]
    bindings = inputs["bindings"]
    scenarios = inputs.get("scenarios", REFERENCE_SCENARIOS)

    base_receipt = reconcile_bronchiectasis_synthetic_profile(
        profile, hierarchy, bindings, created_at=created_at
    )
    scenario_results = run_bronchiectasis_synthetic_scenarios(
        profile, hierarchy, bindings, scenarios, created_at=created_at
    )

    denominator = float(base_receipt["denominator"])
    scenario_rows: list[dict[str, Any]] = []

    for spec, executed in zip(scenarios, scenario_results["scenarios"], strict=True):
        cases = float(executed["estimated_attributable_cases"])
        rate = float(spec.get("exacerbation_rate", 0.8))
        eligibility = float(spec.get("treatment_eligibility_fraction", 0.80))
        annual_exacerbations = round(cases * rate, 2)
        treatment_eligible_cases = round(cases * eligibility, 2)

        scenario_rows.append(
            {
                "scenario_id": executed["scenario_id"],
                "label": spec.get("label", executed["scenario_id"]),
                "description": spec.get("description", ""),
                "multi_aetiology_fraction": executed["multi_aetiology_fraction"],
                "unknown_fraction": executed["unknown_fraction"],
                "transport_multiplier": executed["transport_multiplier"],
                "estimated_attributable_cases": round(cases, 2),
                "proportion_of_denominator": round(cases / denominator, 4),
                "annual_expected_exacerbations": annual_exacerbations,
                "targeted_treatment_eligible_cases": treatment_eligible_cases,
            }
        )

    case_estimates = [row["estimated_attributable_cases"] for row in scenario_rows]

    core_results: dict[str, Any] = {
        "demonstrator_id": "011-bronchiectasis-demonstrator",
        "protocol_id": "RBC-P003",
        "pipeline_version": "1.0.0-reference",
        "created_at": created_at,
        "base_receipt": base_receipt,
        "scenarios_evaluated_count": len(scenario_rows),
        "scenarios": scenario_rows,
        "reference_range": {
            "minimum_cases": min(case_estimates),
            "maximum_cases": max(case_estimates),
            "minimum_proportion": round(min(case_estimates) / denominator, 4),
            "maximum_proportion": round(max(case_estimates) / denominator, 4),
        },
        "conservation_summary": {
            "denominator": denominator,
            "exclusive_sum": base_receipt["exclusive_composition"]["value"],
            "multi_aetiology_cases": base_receipt["multi_aetiology_count"],
            "unknown_cases": base_receipt["unknown_count"],
            "unaccounted_cases": base_receipt["unaccounted_count"],
            "conservation_verified": (
                base_receipt["exclusive_composition"]["value"]
                + base_receipt["multi_aetiology_count"]
                + base_receipt["unknown_count"]
                + base_receipt["unaccounted_count"]
                == denominator
            ),
        },
        "limitations": [
            "All inputs and outputs are synthetic reference artefacts for software assurance.",
            (
                "Scenario allocations are structural model assumptions, not empirical "
                "medical evidence."
            ),
            (
                "Transport multipliers model hypothetical transfer and are not calibrated to "
                "any clinical jurisdiction."
            ),
            "No clinical diagnosis, patient prognosis, or therapeutic recommendation is made.",
        ],
        "claims": {
            "empirical_activation": False,
            "clinical_interpretation": False,
            "contract_frozen": True,
            "scope_reference_demonstrator_only": True,
        },
    }

    receipt_id = content_id("demo11", core_results)
    return {"schema_version": "1.0.0", "receipt_id": receipt_id, **core_results}


def render_bronchiectasis_reference_report(results: Mapping[str, Any]) -> str:
    """Render a comprehensive GitHub-flavored Markdown report of the demonstrator run."""
    lines: list[str] = []
    lines.append("# Track 011: Bronchiectasis Rare-Aetiology Demonstrator Reference Report")
    lines.append("")
    lines.append(f"**Protocol ID:** `{results.get('protocol_id', 'RBC-P003')}`  ")
    lines.append(f"**Receipt ID:** `{results.get('receipt_id')}`  ")
    lines.append(f"**Created At:** `{results.get('created_at')}`  ")
    lines.append(
        "**Status:** Synthetic reference analysis; no empirical validation or clinical authority."
    )
    lines.append("")
    lines.append("## 1. Executive Summary")
    lines.append("")
    lines.append(
        "This report records the executed synthetic reference analysis for Track 011 "
        "(`011-bronchiectasis-demonstrator`) under protocol RBC-P003. "
        "The demonstrator models a common-disease respiratory phenotype (bronchiectasis) "
        "containing multiple rare aetiologies (e.g. primary ciliary dyskinesia, cystic fibrosis, "
        "primary immunodeficiencies), multi-aetiology overlap, and substantial unexplained "
        "(idiopathic) proportions."
    )
    lines.append("")
    lines.append("## 2. Conservation Accounting")
    lines.append("")
    cons = results.get("conservation_summary", {})
    lines.append("| Quantity | Cases | Description |")
    lines.append("|---|---|---|")
    lines.append(f"| Denominator | {cons.get('denominator')} | Synthetic population envelope |")
    lines.append(
        f"| Mutually Exclusive Sum | {cons.get('exclusive_sum')} | Conserved exclusive sum |"
    )
    lines.append(
        f"| Multi-Aetiology Cases | {cons.get('multi_aetiology_cases')} | Separate bucket |"
    )
    lines.append(f"| Unknown / Idiopathic | {cons.get('unknown_cases')} | Unclassified bucket |")
    lines.append(f"| Unaccounted Remainder | {cons.get('unaccounted_cases')} | Exact remainder |")
    lines.append("")
    lines.append(f"**Conservation Check Passed:** `{cons.get('conservation_verified')}`")
    lines.append("")
    lines.append("## 3. Evaluated Scenarios and Structural Sensitivity")
    lines.append("")
    lines.append(
        "| Scenario ID | Multi Fraction | Unknown Fraction | Transport Mult "
        "| Attributable Cases | Denom Proportion | Exacerbations | Treatment Eligible |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")

    for row in results.get("scenarios", []):
        lines.append(
            f"| `{row['scenario_id']}` | {row['multi_aetiology_fraction']} | "
            f"{row['unknown_fraction']} | {row['transport_multiplier']} | "
            f"**{row['estimated_attributable_cases']}** | {row['proportion_of_denominator']:.4f} | "
            f"{row['annual_expected_exacerbations']} | {row['targeted_treatment_eligible_cases']} |"
        )

    lines.append("")
    ref = results.get("reference_range", {})
    lines.append("## 4. Reference Range")
    lines.append("")
    lines.append(
        f"- **Minimum Estimated Attributable Cases:** `{ref.get('minimum_cases')}` "
        f"({ref.get('minimum_proportion', 0) * 100:.2f}% of denominator)"
    )
    lines.append(
        f"- **Maximum Estimated Attributable Cases:** `{ref.get('maximum_cases')}` "
        f"({ref.get('maximum_proportion', 0) * 100:.2f}% of denominator)"
    )
    lines.append("")
    lines.append("## 5. Methodological Limitations")
    lines.append("")
    for item in results.get("limitations", []):
        lines.append(f"- {item}")
    lines.append("")

    return "\n".join(lines)


def render_bronchiectasis_reference_csv(results: Mapping[str, Any]) -> str:
    """Export the evaluated scenario matrix to standard CSV."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    writer.writerow(
        [
            "scenario_id",
            "label",
            "multi_aetiology_fraction",
            "unknown_fraction",
            "transport_multiplier",
            "estimated_attributable_cases",
            "proportion_of_denominator",
            "annual_expected_exacerbations",
            "targeted_treatment_eligible_cases",
            "description",
        ]
    )

    for row in results.get("scenarios", []):
        writer.writerow(
            [
                row["scenario_id"],
                row["label"],
                row["multi_aetiology_fraction"],
                row["unknown_fraction"],
                row["transport_multiplier"],
                row["estimated_attributable_cases"],
                row["proportion_of_denominator"],
                row["annual_expected_exacerbations"],
                row["targeted_treatment_eligible_cases"],
                row["description"],
            ]
        )

    return output.getvalue()
