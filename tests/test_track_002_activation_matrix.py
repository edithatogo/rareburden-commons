from __future__ import annotations

from pathlib import Path

import yaml

MATRIX = Path(__file__).parents[1] / "docs/track-002-activation-matrix.yml"
FINDINGS = Path(__file__).parents[1] / "docs/track-002-findings-disposition.yml"


def test_activation_matrix_is_per_row_and_fail_closed() -> None:
    document = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert document["activation_policy"] == "per_estimand_row"
    assert document["default_unresolved_posture"] == "metadata_hash_only"
    assert document["status"] == "bounded_analytical_activation"
    assert all(row["required_receipts"] for row in document["rows"])
    assert all(row["evidence_state"] for row in document["rows"])

    by_id = {row["estimand_id"]: row for row in document["rows"]}
    for estimand in ("E-ORPHA-DESCRIPTIVE-01", "E-WPP-POP-01", "E-WB-POP-PROBE"):
        assert by_id[estimand]["evidence_state"]["source_change_exercise"] == (
            "complete_2026_08_20_hash_stable"
        )
    assert by_id["E-WHO-COMP-2000"]["evidence_state"]["publisher_third_party_rights"] == ("pending")


def test_activation_matrix_matches_exact_private_archive_dispositions() -> None:
    document = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    rows = {row["estimand_id"]: row for row in document["rows"]}

    assert rows["E-ORPHA-DESCRIPTIVE-01"]["raw_bytes"].startswith(
        "private_archive_present_under_cc_by_4_0"
    )
    assert rows["E-WPP-POP-01"]["raw_bytes"].startswith(
        "private_archive_present_under_cc_by_3_0_igo"
    )
    assert rows["E-WHO-COMP-2000"]["raw_bytes"] == (
        "withheld_from_hugging_face; metadata_and_hash_only"
    )
    assert rows["E-ORPHA-DESCRIPTIVE-01"]["activation"] == "active_bounded"
    assert rows["E-WPP-POP-01"]["activation"] == "active_bounded"
    assert rows["E-WPP-POP-01"]["geography"] == ["Australia", "New Zealand"]
    assert rows["E-WPP-POP-01"]["years"] == [2000, 2021]
    assert rows["E-WPP-POP-01"]["variant"] == "medium"
    assert rows["E-WHO-COMP-2000"]["activation"] == "candidate_only"
    assert rows["E-WB-POP-PROBE"]["activation"] == "probe_only"


def test_findings_dispositions_are_bounded() -> None:
    document = yaml.safe_load(FINDINGS.read_text(encoding="utf-8"))
    allowed = set(document["allowed_dispositions"])
    assert all(row["disposition"] in allowed for row in document["findings"])
    assert all(row["evidence"] and row["residual_risk"] for row in document["findings"])
