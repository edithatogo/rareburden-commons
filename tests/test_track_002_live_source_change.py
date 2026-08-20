from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts/observe_track_002_source_change.py"
SPEC = importlib.util.spec_from_file_location("observe_track_002_source_change", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Response:
    def __init__(self, body: bytes, url: str) -> None:
        self.body = body
        self.url = url
        self.status = 200

    def __enter__(self) -> Response:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def geturl(self) -> str:
        return self.url

    def read(self, _size: int) -> bytes:
        body, self.body = self.body, b""
        return body


def _source(tmp_path: Path, candidates: list[dict[str, Any]]) -> Path:
    path = tmp_path / "candidates.json"
    path.write_text(
        json.dumps({"schema_version": "1.0.0", "candidates": candidates}), encoding="utf-8"
    )
    return path


def test_observer_records_stable_and_changed_without_activation(tmp_path: Path) -> None:
    stable = b"stable"
    changed = b"changed"
    candidates = [
        {
            "source_id": "stable",
            "release_id": "v1",
            "requested_url": "https://www.orphadata.com/stable",
            "expected_sha256": hashlib.sha256(stable).hexdigest(),
        },
        {
            "source_id": "changed",
            "release_id": "v1",
            "requested_url": "https://api.worldbank.org/changed",
            "expected_sha256": "0" * 64,
        },
    ]
    bodies = iter([stable, changed])

    def opener(request: Any, **_kwargs: Any) -> Response:
        return Response(next(bodies), request.full_url)

    result = MODULE.observe(
        _source(tmp_path, candidates),
        observed_at_utc="2026-08-20T00:00:00+00:00",
        interval=0,
        opener=opener,
    )
    assert result["summary"] == {"stable": 1, "changed": 1, "unavailable": 0}
    assert result["activation_permitted"] is False
    assert result["records"][0]["incident_required"] is False
    assert result["records"][1]["incident_required"] is True
    assert all(item["source_bytes_retained"] is False for item in result["records"])


@pytest.mark.parametrize(
    "candidate, message",
    [
        (
            {
                "source_id": "unsafe",
                "release_id": "v1",
                "requested_url": "https://example.com/file",
                "expected_sha256": "0" * 64,
            },
            "untrusted candidate URL",
        ),
        (
            {
                "source_id": "bad-hash",
                "release_id": "v1",
                "requested_url": "https://www.orphadata.com/file",
                "expected_sha256": "not-a-hash",
            },
            "invalid expected SHA-256",
        ),
    ],
)
def test_observer_rejects_unsafe_candidates(
    tmp_path: Path, candidate: dict[str, Any], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        MODULE.observe(_source(tmp_path, [candidate]), interval=0)


def test_checked_in_candidate_set_is_exact_and_inactive() -> None:
    document = json.loads(
        (ROOT / "docs/track-002-live-source-change-candidates-2026-08-20.json").read_text(
            encoding="utf-8"
        )
    )
    candidates = document["candidates"]
    assert len(candidates) == 5
    assert len({item["source_id"] for item in candidates}) == 5
    assert all(len(item["expected_sha256"]) == 64 for item in candidates)


def test_checked_in_live_exercise_is_stable_but_non_authorizing() -> None:
    result = json.loads(
        (ROOT / "docs/track-002-live-source-change-exercise-2026-08-20.json").read_text(
            encoding="utf-8"
        )
    )
    assert result["summary"] == {"changed": 0, "stable": 5, "unavailable": 0}
    assert result["activation_permitted"] is False
    assert len(result["records"]) == 5
    assert all(item["expected_sha256"] == item["observed_sha256"] for item in result["records"])
    assert all(item["source_bytes_retained"] is False for item in result["records"])
    assert all(item["activation_permitted"] is False for item in result["records"])


@pytest.mark.parametrize("failure", ["redirect", "oversized"])
def test_observer_records_fail_closed_transport_incidents(tmp_path: Path, failure: str) -> None:
    body = b"stable"
    candidate = {
        "source_id": "candidate",
        "release_id": "v1",
        "requested_url": "https://www.orphadata.com/file",
        "expected_sha256": hashlib.sha256(body).hexdigest(),
    }

    def opener(request: Any, **_kwargs: Any) -> Response:
        response = Response(body, request.full_url)
        if failure == "redirect":
            response.url = "https://example.com/file"
        else:
            response.body = b"x" * (MODULE._MAX_BYTES + 1)
        return response

    result = MODULE.observe(_source(tmp_path, [candidate]), interval=0, opener=opener)

    assert result["summary"] == {"stable": 0, "changed": 0, "unavailable": 1}
    record = result["records"][0]
    assert record["incident_required"] is True
    assert record["source_bytes_retained"] is False
    assert record["activation_permitted"] is False
