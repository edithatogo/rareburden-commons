from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "observe_track_007_live_metadata",
    ROOT / "scripts" / "observe_track_007_live_metadata.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_observation_retains_no_description_and_never_excludes() -> None:
    reconciliation = {
        "records": [
            {
                "identifier_key": "github:owner/repo",
                "identifier": "owner/repo",
                "reconciliation_state": "pending_metadata_retrieval",
            }
        ]
    }

    def fixture(_url: str, _timeout: int) -> tuple[bytes, int, str]:
        body = json.dumps(
            {
                "name": "repo",
                "html_url": "https://github.com/owner/repo",
                "description": "Rare disease burden measurement dataset",
            }
        ).encode()
        return body, 200, "https://api.github.com/repos/owner/repo"

    report = MODULE.observe(
        json.dumps(reconciliation).encode(),
        fetch_record=fixture,
        observed_at_utc="2026-08-16T00:00:00Z",
    )
    item = report["observations"][0]
    assert item["screening_decision"] == "include_for_content_assessment"
    assert item["description_retained"] is False
    assert "description" not in item


def test_http_failure_remains_pending() -> None:
    reconciliation = {
        "records": [
            {
                "identifier_key": "zenodo:123",
                "identifier": "123",
                "reconciliation_state": "pending_metadata_retrieval",
            }
        ]
    }

    def fixture(url: str, _timeout: int) -> tuple[bytes, int, str]:
        return b"not found", 404, url

    report = MODULE.observe(json.dumps(reconciliation).encode(), fetch_record=fixture)
    assert report["observations"][0]["screening_decision"] == "pending_observation_retry"


def test_committed_observation_accounts_for_every_live_only_identifier() -> None:
    reconciliation = json.loads(
        (ROOT / "docs/track-007-live-reconciliation-2026-08-16.json").read_text()
    )
    report = json.loads(
        (ROOT / "docs/track-007-live-metadata-observations-2026-08-16.json").read_text()
    )
    assert report["observation_count"] == reconciliation["counts"]["pending_metadata_retrieval"]
    assert sum(report["counts"].values()) == report["observation_count"]
    assert all(item["screening_decision"] != "exclude" for item in report["observations"])
    serialized = json.dumps(report).casefold()
    assert '"description"' not in serialized
    assert '"abstract"' not in serialized
    assert '"full_text"' not in serialized
