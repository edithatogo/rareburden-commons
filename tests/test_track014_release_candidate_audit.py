import json
from pathlib import Path

import pytest

from scripts.check_track014_release_candidate_audit import (
    Track014AuditError,
    validate,
)

ROOT = Path(__file__).resolve().parents[1]


def test_exact_candidate_audit_passes_and_keeps_release_gates_pending() -> None:
    result = validate(ROOT)

    assert result["status"] == "exact_candidate_audit_pass_with_release_gates_pending"
    assert result["candidate"]["commit"] == "110da59060d1183f82b7e54e388ca18225c5e88d"
    assert result["claims"]["release_authorized"] is False
    assert result["claims"]["public_artifact_verified"] is False


def test_exact_candidate_audit_rejects_output_drift(tmp_path: Path) -> None:
    relatives = [
        "manifests/atlas/track-014-bounded-release-surface-2026-08-16.json",
        "docs/track-014-accessibility-checklist.md",
        "docs/track-014-evidence-presentation-contract-2026-08-21.yml",
        "docs/track-014-owner-installed-reproduction-receipt-2026-08-22.json",
        "docs/reviews/track-014-reference-output-panel-2026-09-06.yml",
        "results/track-014-reference-2026-09-06/reference-report.md",
        "results/track-014-reference-2026-09-06/reference-results.json",
        "results/track-014-reference-2026-09-06/reference-tables.csv",
    ]
    surface = json.loads((ROOT / relatives[0]).read_text(encoding="utf-8"))
    relatives.extend(item["artifact"] for item in surface["dependency_artifacts"])
    for relative in relatives:
        source = ROOT / relative
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())

    output = tmp_path / "results/track-014-reference-2026-09-06/reference-report.md"
    output.write_text(output.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")

    with pytest.raises(Track014AuditError, match="reference artifact hash mismatch"):
        validate(tmp_path)
