from __future__ import annotations

from pathlib import Path

import yaml

MATRIX = Path(__file__).parents[1] / "docs/track-002-activation-matrix.yml"
FINDINGS = Path(__file__).parents[1] / "docs/track-002-findings-disposition.yml"


def test_activation_matrix_is_per_row_and_fail_closed() -> None:
    document = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert document["activation_policy"] == "per_estimand_row"
    assert document["default_unresolved_posture"] == "metadata_hash_only"
    assert all(row["activation"] != "active" for row in document["rows"])
    assert all(row["required_receipts"] for row in document["rows"])


def test_findings_dispositions_are_bounded() -> None:
    document = yaml.safe_load(FINDINGS.read_text(encoding="utf-8"))
    allowed = set(document["allowed_dispositions"])
    assert all(row["disposition"] in allowed for row in document["findings"])
    assert all(row["evidence"] and row["residual_risk"] for row in document["findings"])
