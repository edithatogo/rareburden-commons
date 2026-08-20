from __future__ import annotations

import json

from scripts.capture_track_007_v021_pilot import (
    _identifiers,
    capture,
)


def test_provider_identifier_parsing_ignores_incomplete_rows() -> None:
    assert _identifiers(
        "github",
        {"items": [{"full_name": "owner/repo"}, {}, {"id": 42}]},
    ) == ["owner/repo", "42"]
    assert _identifiers(
        "zenodo",
        {"hits": {"hits": [{"id": 7}, {"doi": "10.5281/zenodo.8"}, {}]}},
    ) == ["7", "10.5281/zenodo.8"]


def test_pilot_completes_bounded_cells_without_retaining_response_bodies(
    monkeypatch, tmp_path
) -> None:
    def fake_request(provider: str, query: str) -> tuple[str, bytes, int, str]:
        return (
            f"https://example.test/{provider}",
            json.dumps({"items": [{"DOI": "10.1/example"}]}).encode(),
            200,
            f"https://example.test/{provider}",
        )

    monkeypatch.setattr("scripts.capture_track_007_v021_pilot._request", fake_request)
    monkeypatch.setattr("scripts.capture_track_007_v021_pilot.time.sleep", lambda _: None)

    result = capture(output=tmp_path / "nested" / "pilot.json")

    assert result["status"] == "bounded_observation_complete"
    assert result["cells_observed"] == result["planned_cells"] == 48
    assert result["raw_response_retention"] == "none"
    assert all("response_sha256" in observation for observation in result["observations"])
    assert all("response_body" not in observation for observation in result["observations"])


def test_pilot_stops_fail_closed_on_transport_failure(monkeypatch, tmp_path) -> None:
    def failing_request(provider: str, query: str) -> tuple[str, bytes, int, str]:
        raise TimeoutError("transport unavailable")

    monkeypatch.setattr("scripts.capture_track_007_v021_pilot._request", failing_request)

    result = capture(output=tmp_path / "pilot.json")

    assert result["status"] == "stopped_fail_closed"
    assert result["stop_reason"] == "provider_or_transport_failure"
    assert result["cells_observed"] == 1
    assert result["observations"][0]["error_type"] == "TimeoutError"
    assert "error" not in result["observations"][0]
