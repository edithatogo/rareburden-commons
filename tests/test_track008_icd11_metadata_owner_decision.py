from pathlib import Path

from rareburden.schema import load_mapping, validate_instance

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "docs/decisions/2026-08-21-track-008-icd11-metadata-owner-decision.yml"
SCHEMA = ROOT / "schemas/agent-owner-decision-packet.schema.json"


def test_icd11_metadata_owner_decision_is_exact_and_preserves_dissent() -> None:
    decision = load_mapping(DECISION)
    validate_instance(decision, load_mapping(SCHEMA), label="ICD-11 metadata decision")
    assert decision["candidate"]["commit"] == "60b46eb77c2afb3e495499aa504a13977605dcb2"
    assert decision["recommendation"]["option_id"] == "A"
    assert decision["owner_decision"]["selected_option_id"] == "A"
    assert any("GHED" in finding for finding in decision["dissent"])
    assert any("redistribute" in boundary for boundary in decision["evidence"]["cannot_infer"])
