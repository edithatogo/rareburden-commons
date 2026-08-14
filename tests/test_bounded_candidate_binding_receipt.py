from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_bounded_candidate_binding_is_not_a_release_receipt() -> None:
    document = yaml.safe_load(
        (ROOT / "docs/bounded-candidate-binding-receipt-2026-08-03.yml").read_text()
    )
    assert document["status"] == "owner_bound_preparation_only"
    assert len(document["peeled_commit"]) == 40
    assert "not an independent" in document["owner_authority_boundary"]
    assert "release-authority decision" in document["required_before_release"]
