from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from scripts.archive_who_icd_inventory import (
    ICDClient,
    Observation,
    _retry_delay,
    _trusted_url,
    enumerate_inventory,
)


def _observation(endpoint: str, document: dict[str, Any], status: int = 200) -> Observation:
    payload = json.dumps(document, sort_keys=True).encode()
    import hashlib

    return Observation(
        endpoint=endpoint,
        language="en",
        status=status,
        size=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        payload=payload,
    )


class FakeClient:
    def __init__(self) -> None:
        self.documents = {
            "/icd/entity": {
                "releaseId": "2026-01",
                "allReleases": [
                    "http://id.who.int/icd/entity",
                    "http://id.who.int/icd/entity?version=2025-01",
                ],
            },
            "/icd/release/11/2026-01/mms": {
                "releaseDate": "2026-01-17",
                "availableLanguages": ["en", "fr", "en"],
                "prereleaseLanguages": ["fr"],
            },
            "/icd/release/11/2026-01/icf": {
                "releaseDate": "2026-01-17",
                "availableLanguages": ["en"],
            },
            "/icd/release/11/2025-01/mms": {
                "releaseDate": "2025-01-24",
                "availableLanguages": ["en"],
            },
            "/icd/release/10": {"release": ["http://id.who.int/icd/release/10/2019"]},
            "/icd/release/10/2019": {"releaseDate": "2020-02-01"},
        }

    def get(self, endpoint: str, *, language: str = "en") -> Observation:
        del language
        if endpoint == "/icd/release/11/2025-01/icf":
            return _observation(endpoint, {"error": "not found"}, status=404)
        return _observation(endpoint, self.documents[endpoint])


def test_inventory_enumerates_releases_languages_and_explicit_gaps():
    inventory, observations = enumerate_inventory(
        FakeClient(),  # type: ignore[arg-type]
        observed_at="2026-08-16T00:00:00+00:00",
    )
    rows = {
        (item["classification"], item["release_id"]): item for item in inventory["classifications"]
    }
    assert rows[("who-fic-foundation", "2026-01")]["available_languages"] == []
    assert rows[("icd11-mms", "2026-01")]["available_languages"] == ["en", "fr"]
    assert rows[("icd11-mms", "2026-01")]["prerelease_languages"] == ["fr"]
    assert rows[("icd11-icf", "2025-01")]["http_status"] == 404
    assert rows[("icd10", "2019")]["language_evidence"] == ("not_exposed_by_release_endpoint")
    assert inventory["claims"]["complete_who_fic_family"] is False
    assert inventory["rights"]["public_raw_redistribution"] is False
    assert all(
        item["raw_route"] == "private_licensed_archive_only" for item in inventory["observations"]
    )
    assert len(observations) == 7


def test_client_rejects_untrusted_or_non_icd_routes():
    with pytest.raises(ValueError, match="untrusted WHO"):
        _trusted_url(
            "https://example.org/icd/entity",
            host="id.who.int",
            path_prefix="/icd/",
        )
    with pytest.raises(ValueError, match="untrusted WHO"):
        _trusted_url(
            "https://id.who.int/icd/entity?unexpected=true",
            host="id.who.int",
            path_prefix="/icd/",
        )
    client = ICDClient(
        token_url="https://icdaccessmanagement.who.int/connect/token",
        api_base="https://id.who.int",
        client_id="id",
        client_secret="secret",
        request_interval=0,
    )
    with pytest.raises(ValueError, match="/icd/ path"):
        client.get("/fhir/CodeSystem")


def test_retry_after_is_bounded_and_defaults_exponentially():
    assert _retry_delay({"Retry-After": "1"}, 0) == 2
    assert _retry_delay({"Retry-After": "9999"}, 0) == 900
    assert _retry_delay({}, 3) == 16


def test_inventory_fails_closed_on_untrusted_icd10_release():
    client = FakeClient()
    client.documents["/icd/release/10"] = {"release": ["https://evil.example/icd/release/10/2019"]}
    with pytest.raises(RuntimeError, match="untrusted"):
        enumerate_inventory(
            client,  # type: ignore[arg-type]
            observed_at="2026-08-16T00:00:00+00:00",
        )


def test_checked_in_who_inventory_is_metadata_only_and_bounded():
    inventory = json.loads(
        Path("manifests/classifications/who-icd-api-inventory-2026-08-16.json").read_text(
            encoding="utf-8"
        )
    )
    assert inventory["rights"] == {
        "public_manifest": "metadata_hashes_only",
        "raw_api_responses": "private_licensed_archive_only",
        "public_raw_redistribution": False,
    }
    assert inventory["claims"] == {
        "complete_api_graph": False,
        "complete_who_fic_family": False,
        "national_editions_included": False,
        "production_activation": False,
    }
    assert not any("Authorization" in json.dumps(item) for item in inventory["observations"])
    assert {item["classification"] for item in inventory["classifications"]} >= {
        "icd11-mms",
        "icd11-icf",
        "icd10",
    }
