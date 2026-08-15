from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.archive_mondo_release_batch import (
    mondo_releases,
    remote_lfs_sha256,
    select_assets,
    verify_remote_object,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/classifications/public-history-frontier-2026-08-16.json"


def test_exact_frontier_and_bounded_asset_selection() -> None:
    releases = mondo_releases(json.loads(MANIFEST.read_text(encoding="utf-8")))
    release, assets = select_assets(releases, release_index=0, asset_start=0, asset_count=1)
    assert release == "v2026-08-04"
    assert assets[0]["name"] == "README.md"


def test_selection_rejects_empty_or_out_of_range() -> None:
    releases = mondo_releases(json.loads(MANIFEST.read_text(encoding="utf-8")))
    with pytest.raises(ValueError, match="outside"):
        select_assets(releases, release_index=120, asset_start=0, asset_count=1)
    with pytest.raises(ValueError, match="positive"):
        select_assets(releases, release_index=0, asset_start=0, asset_count=0)


def test_frontier_rejects_missing_release() -> None:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    mondo = next(item for item in document["observations"] if item["family"] == "mondo")
    mondo["records"].pop()
    with pytest.raises(ValueError, match="120-release"):
        mondo_releases(document)


def test_remote_lfs_digest_supports_client_shapes() -> None:
    mapping_shape = type("Sibling", (), {"lfs": {"oid": "a" * 64}})()
    object_shape = type("Sibling", (), {"lfs": type("Lfs", (), {"sha256": "b" * 64})()})()
    assert remote_lfs_sha256(mapping_shape) == "a" * 64
    assert remote_lfs_sha256(object_shape) == "b" * 64


def test_non_lfs_remote_object_is_redownloaded_and_hashed(tmp_path: Path) -> None:
    payload = tmp_path / "README.md"
    payload.write_bytes(b"exact publisher bytes")
    expected = __import__("hashlib").sha256(payload.read_bytes()).hexdigest()
    item = type("Sibling", (), {"size": payload.stat().st_size, "lfs": None})()
    assert verify_remote_object(
        item,
        expected_size=payload.stat().st_size,
        expected_sha256=expected,
        download_non_lfs=lambda: payload,
    )


def test_non_lfs_remote_object_mismatch_fails_closed(tmp_path: Path) -> None:
    payload = tmp_path / "README.md"
    payload.write_bytes(b"different bytes")
    item = type("Sibling", (), {"size": payload.stat().st_size, "lfs": None})()
    assert not verify_remote_object(
        item,
        expected_size=payload.stat().st_size,
        expected_sha256="0" * 64,
        download_non_lfs=lambda: payload,
    )


def test_non_lfs_existing_remote_object_can_be_reused(tmp_path: Path) -> None:
    payload = tmp_path / "README.md"
    payload.write_bytes(b"previously uploaded exact bytes")
    expected = __import__("hashlib").sha256(payload.read_bytes()).hexdigest()
    existing = type("Sibling", (), {"size": payload.stat().st_size, "lfs": None})()
    assert verify_remote_object(
        existing,
        expected_size=payload.stat().st_size,
        expected_sha256=expected,
        download_non_lfs=lambda: payload,
    )
