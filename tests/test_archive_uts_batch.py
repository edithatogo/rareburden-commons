from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.archive_uts_batch import _load_family, _retry_delay


def _manifest(release_type: str = "umls-full-release") -> dict:
    return {
        "families": [
            {
                "release_type": release_type,
                "releases": [
                    {
                        "fileName": "umls-2026AA-full.zip",
                        "releaseVersion": "2026AA",
                        "releaseDate": "2026-05-03",
                        "downloadUrl": (
                            "https://download.nlm.nih.gov/umls/kss/2026AA/umls-2026AA-full.zip"
                        ),
                        "releaseType": "UMLS Full Release",
                        "product": "UMLS",
                        "current": True,
                    }
                ],
            }
        ]
    }


def test_load_family_accepts_exact_nlm_release(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(_manifest()), encoding="utf-8")
    assert _load_family(path, "umls-full-release")[0]["releaseVersion"] == "2026AA"


def test_load_family_accepts_historical_release_without_current_flag(tmp_path):
    document = _manifest()
    del document["families"][0]["releases"][0]["current"]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    assert _load_family(path, "umls-full-release")[0]["releaseVersion"] == "2026AA"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("fileName", "../secret.zip"),
        ("releaseVersion", "../2026AA"),
        ("downloadUrl", "https://example.org/umls.zip"),
    ],
)
def test_load_family_rejects_unsafe_release_fields(tmp_path, field, value):
    document = _manifest()
    document["families"][0]["releases"][0][field] = value
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError):
        _load_family(path, "umls-full-release")


def test_load_family_rejects_unknown_family(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(_manifest()), encoding="utf-8")
    with pytest.raises(ValueError):
        _load_family(path, "unknown")


def test_checked_in_inventory_validates_every_release_family():
    manifest = Path("manifests/uts/all-release-families-2026-08-15.json")
    document = json.loads(manifest.read_text(encoding="utf-8"))
    families = document["families"]
    assert len(families) == 14
    assert sum(len(family["releases"]) for family in families) == 2451
    for family in families:
        assert _load_family(manifest, family["release_type"])


def test_retry_delay_honours_server_header_and_bounds_fallback():
    assert _retry_delay({"Retry-After": "17"}, 0) == 17
    assert _retry_delay({"Retry-After": "9999"}, 0) == 900
    assert _retry_delay({}, 0) == 2
    assert _retry_delay({}, 20) == 300
