from __future__ import annotations

import io
import json
from email.message import Message
from pathlib import Path
from typing import Any

import pytest

from scripts.observe_who_fic_authorities import _validate_source, observe

SOURCE = Path("manifests/classifications/who-fic-authority-sources-2026-08-16.json")


class FakeResponse:
    def __init__(self, url: str) -> None:
        self._url = url
        self.status = 200
        self.headers = Message()
        self.headers["Content-Type"] = "text/html"
        self._stream = io.BytesIO(b"official landing page")

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def geturl(self) -> str:
        return self._url


def test_ledger_covers_bounded_who_fic_and_country_authority_scope():
    ledger = json.loads(SOURCE.read_text(encoding="utf-8"))
    records = _validate_source(ledger)
    ids = {record["id"] for record in records}
    assert {"who-icf", "who-icf-cy", "who-ichi", "who-icd-o"} <= ids
    assert {
        "us-icd10-cm",
        "au-icd10-am",
        "ca-icd10-ca",
        "de-icd10-gm",
        "gb-england-icd10",
        "nl-icd10-translation",
        "se-icd10-se",
        "nz-icd10-am-adoption",
    } <= ids
    assert all(record["artifact_route"] != "public_raw" for record in records)
    assert "not a global census" in ledger["scope_statement"]


def test_observer_hashes_pages_without_retaining_bodies(tmp_path: Path):
    ledger = json.loads(SOURCE.read_text(encoding="utf-8"))
    ledger["who_fic"] = ledger["who_fic"][:1]
    ledger["national_authorities"] = []
    source = tmp_path / "source.json"
    source.write_text(json.dumps(ledger), encoding="utf-8")

    def opener(request: Any, *, timeout: int) -> FakeResponse:
        assert timeout == 60
        return FakeResponse(request.full_url)

    result = observe(source, interval=0, opener=opener)
    assert result["claims"] == {
        "global_completeness": False,
        "language_completeness": False,
        "artifact_rights": False,
        "source_bytes_archived": False,
        "production_activation": False,
    }
    assert result["observations"][0]["body_retained"] is False
    assert result["observations"][0]["bytes_observed"] == 21
    assert result["observations"][0]["sha256"]


def test_ledger_rejects_untrusted_host_and_public_raw_route():
    ledger = json.loads(SOURCE.read_text(encoding="utf-8"))
    ledger["who_fic"][0]["source_url"] = "https://example.org/classification"
    with pytest.raises(ValueError, match="untrusted"):
        _validate_source(ledger)
    ledger = json.loads(SOURCE.read_text(encoding="utf-8"))
    ledger["who_fic"][0]["artifact_route"] = "public_raw"
    with pytest.raises(ValueError, match="unsafe archive route"):
        _validate_source(ledger)


def test_ledger_has_required_provenance_fields_and_explicit_unknown_languages():
    ledger = json.loads(SOURCE.read_text(encoding="utf-8"))
    records = _validate_source(ledger)
    for record in records:
        assert all(
            record[field]
            for field in (
                "classification",
                "country_or_area",
                "languages",
                "version_or_release",
                "authority",
                "source_url",
                "terms_state",
            )
        )
    unknown = [record for record in records if record["languages"] == ["not_enumerated"]]
    assert unknown


def test_checked_observations_bind_every_seed_and_keep_claims_fail_closed():
    ledger = json.loads(SOURCE.read_text(encoding="utf-8"))
    observations = json.loads(
        Path("manifests/classifications/who-fic-authority-observations-2026-08-16.json").read_text(
            encoding="utf-8"
        )
    )
    expected_ids = {record["id"] for record in ledger["who_fic"] + ledger["national_authorities"]}
    assert {item["id"] for item in observations["observations"]} == expected_ids
    assert observations["claims"] == {
        "global_completeness": False,
        "language_completeness": False,
        "artifact_rights": False,
        "source_bytes_archived": False,
        "production_activation": False,
    }
    assert all(item["body_retained"] is False for item in observations["observations"])
    failures = [item for item in observations["observations"] if item["http_status"] != 200]
    assert [(item["id"], item["http_status"]) for item in failures] == [("us-icd10-cm", 403)]
