#!/usr/bin/env python3
"""Validate the simulated Track 015 governance tabletop candidate."""

from __future__ import annotations

import argparse
from pathlib import Path

from rareburden.schema import load_document


class TabletopCandidateError(ValueError):
    """Raised when the tabletop candidate does not fail closed."""


EXPECTED = {
    "source_withdrawal": ("freeze_and_supersede", "source_or_rights_basis_unresolved"),
    "global_ranking_pressure": (
        "publish_bounded_comparison",
        "representation_or_uncertainty_is_obscured",
    ),
    "funder_veto_request": ("reject_veto_and_disclose", "funder_control_cannot_be_removed"),
    "stigmatizing_language": (
        "revise_and_retest",
        "material_stigma_or_context_collapse_remains",
    ),
    "node_disclosure_risk": (
        "block_export_and_reconfigure",
        "custodian_or_disclosure_requirement_unresolved",
    ),
}


def validate(path: Path, root: Path) -> dict[str, object]:
    tabletop = load_document(path)
    if tabletop.get("status") != "simulated_candidate_pending_owner_disposition":
        raise TabletopCandidateError("tabletop must remain pending owner disposition")
    if tabletop.get("independent_or_human_review") is not False:
        raise TabletopCandidateError("tabletop is not independent or human review")
    if tabletop.get("remuneration") != {"model": "unpaid", "amount": 0}:
        raise TabletopCandidateError("tabletop must remain unpaid")
    if tabletop.get("public_or_external_activation") is not False:
        raise TabletopCandidateError("tabletop cannot activate an external path")
    policy_relative = Path(str(tabletop.get("policy_candidate", "")))
    if policy_relative.is_absolute() or ".." in policy_relative.parts:
        raise TabletopCandidateError("policy candidate path is missing or unsafe")
    policy = root / policy_relative
    if not policy.is_file():
        raise TabletopCandidateError("policy candidate path is missing or unsafe")

    scenarios = tabletop.get("scenarios", [])
    ids = [scenario.get("id") for scenario in scenarios]
    if set(ids) != set(EXPECTED) or len(ids) != len(set(ids)):
        raise TabletopCandidateError("required scenarios must be complete and unique")
    for scenario in scenarios:
        expected_recommendation, expected_stop = EXPECTED[scenario["id"]]
        if len(set(scenario.get("perspectives", []))) < 3:
            raise TabletopCandidateError("each scenario requires three perspectives")
        if scenario.get("recommendation") != expected_recommendation:
            raise TabletopCandidateError("scenario recommendation drifted")
        if scenario.get("stop_trigger") != expected_stop:
            raise TabletopCandidateError("scenario stop trigger drifted")
        if scenario.get("recommendation") not in scenario.get("options", []):
            raise TabletopCandidateError("recommendation must reference an option")
    if tabletop.get("owner_disposition") != {"status": "pending"}:
        raise TabletopCandidateError("owner disposition must remain explicitly pending")
    return {
        "status": "simulated_tabletop_candidate_valid",
        "scenario_count": len(scenarios),
        "owner_disposition_pending": True,
        "external_activation": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tabletop", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        result = validate(args.tabletop.resolve(), args.root.resolve())
    except (TabletopCandidateError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"Track 015 tabletop candidate failed: {exc}")
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
