from pathlib import Path

from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "docs/decisions/2026-08-21-source-registry-alignment-owner-decision.yml"
SCHEMA = ROOT / "schemas/agent-owner-decision-packet.schema.json"


def test_source_registry_alignment_owner_decision_is_exact_and_bounded() -> None:
    decision = load_mapping(DECISION)
    validate_instance(decision, load_mapping(SCHEMA), label="source registry decision")
    assert decision["recommendation"]["option_id"] == "A"
    assert decision["owner_decision"]["selected_option_id"] == "A"
    assert any(
        boundary.startswith("raw-data redistribution permission")
        for boundary in decision["evidence"]["cannot_infer"]
    )
    assert decision["candidate"]["commit"] == "43fd917085e8aae747bff58ccde5e04d6cfc774a"
