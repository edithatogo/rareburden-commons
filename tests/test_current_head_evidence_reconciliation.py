from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_reconciliation_packet_records_current_head_artifacts() -> None:
    document = yaml.safe_load(
        (ROOT / "docs/release-candidate-evidence-reconciliation-2026-08-04.yml").read_text()
    )
    assert document["status"] == "reconciliation_preparation_current_head"
    assert all(
        item["status"] == "repository_generated_at_current_head_pending_hosted_binding"
        for item in document["artifacts"]
    )
    assert document["release_authority"] == "pending"
