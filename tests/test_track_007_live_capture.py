from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "track-007-live-capture-coverage-2026-08-15.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_live_capture_report_binds_exact_evidence() -> None:
    report = _load(REPORT)
    assert report["status"] == "bounded_live_capture_complete"
    captures = report["captures"]
    assert isinstance(captures, list)
    assert {item["registry"] for item in captures} == {
        "github",
        "zenodo",
        "huggingface_datasets",
    }
    for item in captures:
        path = ROOT / item["evidence_path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
        evidence = _load(path)
        assert evidence["status"] == "bounded_capture_only"
        assert len(evidence["captures"]) == report["protocol_queries"]
        assert (
            sum(row["occurrences_captured"] for row in evidence["captures"])
            == item["occurrences_captured"]
        )


def test_live_capture_coverage_remains_fail_closed() -> None:
    report = _load(REPORT)
    disposition = report["coverage_disposition"]
    assert disposition["global_representativeness"] == "prohibited"
    assert disposition["comprehensive_landscape_claim"] == "prohibited"
    assert disposition["novelty_claim"] == "provisional"
    zenodo = next(item for item in report["captures"] if item["registry"] == "zenodo")
    assert zenodo["query_runs_at_page_budget"] == report["protocol_queries"]
    huggingface = next(
        item for item in report["captures"] if item["registry"] == "huggingface_datasets"
    )
    assert huggingface["occurrences_captured"] == 0
    assert "No absence-of-datasets" in huggingface["interpretation"]
