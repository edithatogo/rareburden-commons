from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.capture_track_007_pages import CaptureError, PageRequest, capture_query

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "track007_pagination"


def fixture_pages(prefix: str):
    def fetch(request: PageRequest, _timeout: int) -> tuple[bytes, int, str]:
        path = FIXTURES / f"{prefix}-page-{request.page_number}.json"
        return path.read_bytes(), 200, request.url

    return fetch


def test_declared_total_requires_exact_unique_capture() -> None:
    capture = capture_query(
        "github",
        "fixture query",
        page_size=2,
        max_pages=3,
        timeout=1,
        fetch_page=fixture_pages("github-complete"),
        retrieved_at_utc="2026-08-15T00:00:00Z",
    )
    assert capture["pages_captured"] == 2
    assert capture["unique_identifiers_captured"] == 3
    assert capture["stop_reason"] == "provider_total_reached"
    assert capture["capture_complete_for_declared_total"] is True
    assert "does not establish landscape" in capture["claim_boundary"]
    assert all(page["response_sha256"].startswith("sha256:") for page in capture["pages"])
    assert capture["pages"][0]["screening_records"] == [
        {
            "identifier": "org/a",
            "title": "org/a",
            "canonical_url": "",
        },
        {
            "identifier": "org/b",
            "title": "org/b",
            "canonical_url": "",
        },
    ]


def test_page_budget_is_explicitly_incomplete() -> None:
    capture = capture_query(
        "github",
        "fixture query",
        page_size=2,
        max_pages=1,
        timeout=1,
        fetch_page=fixture_pages("github-changed-total"),
    )
    assert capture["stop_reason"] == "page_budget_reached"
    assert capture["capture_complete_for_declared_total"] is False
    assert capture["provider_declared_total"] == 4


def test_changed_total_fails_closed() -> None:
    with pytest.raises(CaptureError, match="declared total changed"):
        capture_query(
            "github",
            "fixture query",
            page_size=2,
            max_pages=3,
            timeout=1,
            fetch_page=fixture_pages("github-changed-total"),
        )


def test_cross_page_duplicate_fails_closed() -> None:
    with pytest.raises(CaptureError, match="repeated identifiers"):
        capture_query(
            "github",
            "fixture query",
            page_size=2,
            max_pages=3,
            timeout=1,
            fetch_page=fixture_pages("github-repeat"),
        )


def test_invalid_json_and_http_status_fail_closed() -> None:
    def invalid_json(request: PageRequest, _timeout: int) -> tuple[bytes, int, str]:
        return b"not-json", 200, request.url

    with pytest.raises(CaptureError, match="invalid JSON"):
        capture_query(
            "zenodo", "fixture", page_size=2, max_pages=1, timeout=1, fetch_page=invalid_json
        )

    def forbidden(request: PageRequest, _timeout: int) -> tuple[bytes, int, str]:
        return b"{}", 403, request.url

    with pytest.raises(CaptureError, match="HTTP 403"):
        capture_query(
            "zenodo", "fixture", page_size=2, max_pages=1, timeout=1, fetch_page=forbidden
        )


def test_malformed_screening_metadata_fails_closed() -> None:
    def malformed(request: PageRequest, _timeout: int) -> tuple[bytes, int, str]:
        body = json.dumps(
            {"total_count": 1, "items": [{"full_name": "org/repo", "name": ["bad"]}]}
        ).encode()
        return body, 200, request.url

    with pytest.raises(CaptureError, match="title is not text"):
        capture_query(
            "github", "fixture", page_size=2, max_pages=1, timeout=1, fetch_page=malformed
        )


def test_capture_schema_fixture_is_fail_closed() -> None:
    evidence = json.loads(
        (ROOT / "docs" / "track-007-pagination-strategy-2026-08-15.json").read_text()
    )
    assert evidence["schema_version"] == "RBC-LAND-007-PAGES-v0.1.0"
    assert evidence["status"] == "strategy_exercised_with_bounded_live_capture"
    assert evidence["production_capture_status"] == "bounded_live_run_complete"
    assert evidence["live_capture_evidence"].endswith("2026-08-15.json")
    assert evidence["claims"]["ecosystem_completeness"] == "prohibited"
    assert evidence["claims"]["captured_page_reproducibility"] == "supported"


def test_cli_writes_new_capture_but_refuses_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "capture.json"
    command = [
        sys.executable,
        str(ROOT / "scripts" / "capture_track_007_pages.py"),
        "--registry",
        "github",
        "--query",
        "fixture query",
        "--page-size",
        "2",
        "--max-pages",
        "3",
        "--fixture-dir",
        str(FIXTURES),
        "--retrieved-at-utc",
        "2026-08-15T00:00:00Z",
        "--output",
        str(output),
    ]
    # The CLI fixture naming contract uses a query hash, so use the checked-in
    # registry-prefixed fixtures through a temporary exact-name projection.
    slug = hashlib.sha256(b"fixture query").hexdigest()[:12]
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    for page in (1, 2):
        (fixture_dir / f"github-{slug}-page-{page}.json").write_bytes(
            (FIXTURES / f"github-complete-page-{page}.json").read_bytes()
        )
    command[command.index(str(FIXTURES))] = str(fixture_dir)
    subprocess.run(command, check=True)
    assert json.loads(output.read_text())["captures"][0]["pages_captured"] == 2
    repeated = subprocess.run(command, capture_output=True, text=True)
    assert repeated.returncode != 0
    assert "refusing to overwrite capture" in repeated.stderr
