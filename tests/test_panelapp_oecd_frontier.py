import hashlib
import json
from pathlib import Path

import pytest

from scripts import probe_panelapp_oecd_frontier as frontier

ROOT = Path(__file__).resolve().parents[1]


def test_panelapp_registry_is_country_aware_and_blocks_uk_api() -> None:
    payload = json.loads(
        (ROOT / "manifests/panelapp/instance-frontier-2026-08-16.json").read_text()
    )
    records = {item["jurisdiction"]: item for item in payload["instances"]}
    assert set(records) == {"AU", "GB"}
    assert records["GB"]["automated_api_capture"] == "disabled_by_robots"
    assert records["GB"]["publisher_authorized_alternative"]["automation"] is False
    assert records["GB"]["publisher_authorized_alternative"]["completeness_claim"] is False
    assert records["AU"]["raw_archive"].startswith("disabled_pending")
    assert records["AU"]["content_licence_inference"] is False
    assert payload["software_licence_is_content_licence"] is False
    assert payload["claims"] == {
        "global_completeness": False,
        "country_representativeness": False,
        "historical_version_completeness": False,
    }


def test_oecd_bytes_fail_closed_until_dataset_disposition() -> None:
    payload = json.loads((ROOT / "manifests/oecd/export-frontier-2026-08-16.json").read_text())
    assert payload["terms_disposition"]["dataset_bytes"].startswith("disabled_until")
    assert payload["metadata_canary"]["raw_archive"] is False
    assert payload["metadata_canary"]["production_activation"] is False
    assert payload["terms_disposition"]["source_tab_third_party_disposition"].startswith(
        "unresolved"
    )


def test_terms_matrix_separates_visibility_automation_and_reuse() -> None:
    payload = json.loads(
        (ROOT / "docs/track-002-panelapp-oecd-terms-matrix-2026-08-16.json").read_text()
    )
    records = {item["source_id"]: item for item in payload["records"]}
    assert (
        "content_redistribution_right" in records["panelapp-australia-home"]["does_not_establish"]
    )
    assert "all_series_OECD_owned" in records["oecd-health-statistics-2026"]["does_not_establish"]
    assert all(value is False for value in payload["global_claims"].values())


def test_rights_router_is_fail_closed() -> None:
    uk = frontier.rights_route("genomics-england-panelapp")
    au = frontier.rights_route("panelapp-australia")
    oecd = frontier.rights_route("oecd-health-statistics-dataflow", exact_content_terms=True)
    assert uk["route"] == "operator_triggered_publisher_download"
    assert uk["automation"] is False
    assert au["route"] == "metadata_hash_only"
    assert au["raw_redistribution"] is False
    assert oecd["route"] == "metadata_hash_only"
    assert oecd["raw_redistribution"] is False


def test_rights_router_requires_exact_oecd_third_party_clearance() -> None:
    clear = frontier.rights_route(
        "oecd-health-statistics-dataflow",
        exact_content_terms=True,
        third_party_clear=True,
    )
    assert clear["route"] == "bounded_data_export"
    assert clear["raw_redistribution"] is True
    with pytest.raises(ValueError, match="no rights route"):
        frontier.rights_route("unknown")


def test_probe_retains_only_hash_and_bounded_panel_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = json.dumps({"count": 263, "next": "page2", "results": [{"id": 1}]}).encode()
    monkeypatch.setattr(
        frontier, "fetch", lambda _url: (body, {"Content-Type": "application/json"}, 200, _url)
    )
    monkeypatch.setattr(frontier.time, "sleep", lambda _delay: None)
    result = frontier.bounded_observation("panelapp-australia", "https://panelapp-aus.org/api/")
    assert result["sha256"] == hashlib.sha256(body).hexdigest()
    assert result["raw_response_retained"] is False
    assert result["bounded_metadata"] == {
        "reported_count": 263,
        "has_next_page": True,
        "page_result_count": 1,
    }
    assert "results" not in result


def test_probe_rejects_insecure_url_and_too_fast_delay() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        frontier.bounded_observation("panelapp-australia", "http://example.test")
    with pytest.raises(ValueError, match="at least one"):
        frontier.bounded_observation(
            "panelapp-australia", "https://panelapp-aus.org", delay_seconds=0
        )


def test_probe_rejects_wrong_host_and_cross_host_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="host"):
        frontier.bounded_observation("panelapp-australia", "https://example.test")
    monkeypatch.setattr(
        frontier,
        "fetch",
        lambda _url: (b"{}", {"Content-Type": "application/json"}, 200, "https://example.test"),
    )
    monkeypatch.setattr(frontier.time, "sleep", lambda _delay: None)
    with pytest.raises(ValueError, match="redirected"):
        frontier.bounded_observation("panelapp-australia", "https://panelapp-aus.org/api/")


def test_fetch_rejects_response_over_byte_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    class Response:
        status = 200

        def __init__(self) -> None:
            self.headers: dict[str, str] = {}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self, size: int) -> bytes:
            return b"x" * size

        def geturl(self) -> str:
            return "https://panelapp-aus.org/api/"

    monkeypatch.setattr(frontier.urllib.request, "urlopen", lambda *_args, **_kwargs: Response())
    with pytest.raises(ValueError, match="byte budget"):
        frontier.fetch("https://panelapp-aus.org/api/", max_bytes=10)
