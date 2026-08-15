from __future__ import annotations

import json

import pytest

from scripts.archive_hf_batch import _load_manifest


def test_archive_manifest_accepts_exact_safe_record(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.org/release.bin",
                    "path": "releases/example/release.bin",
                    "bytes": 3,
                    "sha256": "a" * 64,
                }
            ]
        ),
        encoding="utf-8",
    )
    assert _load_manifest(manifest)[0]["bytes"] == 3


@pytest.mark.parametrize(
    "override",
    [
        {"url": "http://example.org/release.bin"},
        {"path": "../release.bin"},
        {"bytes": -1},
        {"sha256": "unknown"},
    ],
)
def test_archive_manifest_rejects_unsafe_or_unverifiable_records(tmp_path, override):
    record = {
        "url": "https://example.org/release.bin",
        "path": "releases/example/release.bin",
        "bytes": 3,
        "sha256": "a" * 64,
    }
    record.update(override)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([record]), encoding="utf-8")
    with pytest.raises(ValueError):
        _load_manifest(manifest)
