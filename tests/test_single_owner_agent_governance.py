from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_single_owner_agent_governance import GovernanceError, validate, validate_packet

ROOT = Path(__file__).parents[1]
CONTRACT = ROOT / "docs/single-owner-agent-governance.yml"
TEMPLATE = ROOT / "docs/agent-owner-decision-packet-template.yml"


def _document() -> dict[str, object]:
    return copy.deepcopy(yaml.safe_load(CONTRACT.read_text(encoding="utf-8")))


def _write(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "governance.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_prospective_single_owner_governance_is_valid() -> None:
    validate(CONTRACT, ROOT)


@pytest.mark.parametrize(
    ("section", "field", "value", "message"),
    [
        ("agent_panel", "simulation_status", "community_panel", "explicitly simulated"),
        ("agent_panel", "recommendation_is_approval", True, "must not be approval"),
        ("agent_panel", "agents_are_maintainers", True, "cannot hold accountability"),
        ("external_fact_boundary", "unresolved_fact_action", "accept", "fail closed"),
        ("decision_rule", "exact_candidate_binding_required", False, "safeguards"),
        (
            "claims_boundary",
            "metadata_establishes_novelty_partnership_or_community_authority",
            True,
            "non-inference",
        ),
    ],
)
def test_rejects_authority_or_evidence_drift(
    tmp_path: Path, section: str, field: str, value: object, message: str
) -> None:
    document = _document()
    document[section][field] = value
    with pytest.raises(GovernanceError, match=message):
        validate(_write(tmp_path, document), ROOT)


def test_rejects_missing_external_fact_boundary(tmp_path: Path) -> None:
    document = _document()
    document["external_fact_boundary"]["simulation_cannot_create"].remove(
        "patient_or_community_consent"
    )
    with pytest.raises(GovernanceError, match="external fact boundary is incomplete"):
        validate(_write(tmp_path, document), ROOT)


def test_rejects_duplicate_advice_fields(tmp_path: Path) -> None:
    document = _document()
    document["agent_panel"]["required_presentation"].append("options")
    with pytest.raises(GovernanceError, match="must not contain duplicates"):
        validate(_write(tmp_path, document), ROOT)


def test_rejects_additional_accountable_human(tmp_path: Path) -> None:
    document = _document()
    document["owner"]["human_count"] = 2
    with pytest.raises(GovernanceError, match="owner decision authority drifted"):
        validate(_write(tmp_path, document), ROOT)


def test_rejects_backup_owner_or_co_maintainer(tmp_path: Path) -> None:
    document = _document()
    document["continuity"]["backup_owner_or_co_maintainer"] = "named"
    with pytest.raises(GovernanceError, match="continuity boundary drifted"):
        validate(_write(tmp_path, document), ROOT)


def test_all_active_tracks_name_the_sole_accountable_owner() -> None:
    for metadata_path in (ROOT / "conductor" / "tracks").glob("*/metadata.json"):
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        assert metadata["owner_role"] == "Repository owner (sole accountable human)"


def test_packet_requires_owner_decision_when_requested() -> None:
    validate_packet(TEMPLATE, ROOT)
    with pytest.raises(GovernanceError, match="owner decision is required"):
        validate_packet(TEMPLATE, ROOT, require_owner_decision=True)


def test_packet_recommendation_must_reference_an_option(tmp_path: Path) -> None:
    packet = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
    packet["recommendation"]["option_id"] = "C"
    with pytest.raises(GovernanceError, match="recommendation must reference"):
        validate_packet(_write(tmp_path, packet), ROOT)
