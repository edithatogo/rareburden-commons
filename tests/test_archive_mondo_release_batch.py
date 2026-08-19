from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.archive_mondo_release_batch import (
    mondo_releases,
    remote_lfs_sha256,
    resolve_cursor,
    select_assets,
    validate_cursor,
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


def test_committed_cursor_resumes_after_hosted_batch() -> None:
    assert resolve_cursor(None, None) == (1, 7)
    assert resolve_cursor(4, 5) == (4, 5)
    with pytest.raises(ValueError, match="together"):
        resolve_cursor(1, None)


def test_cursor_binds_contiguous_hosted_receipts_fail_closed() -> None:
    cursor = json.loads(
        (ROOT / "manifests/classifications/mondo-archive-cursor-2026-08-16.json").read_text(
            encoding="utf-8"
        )
    )
    validate_cursor(cursor)
    assert len(cursor["observed_archived_assets"]) == 7
    assert sum(item["bytes"] for item in cursor["observed_archived_assets"]) == 726_797_932

    cursor["hosted_receipts"][2]["asset_index"] = 8
    with pytest.raises(ValueError, match="indices 3 through 6"):
        validate_cursor(cursor)


def test_cursor_rejects_completeness_or_noncontiguous_archive_claims() -> None:
    cursor = json.loads(
        (ROOT / "manifests/classifications/mondo-archive-cursor-2026-08-16.json").read_text(
            encoding="utf-8"
        )
    )
    cursor["claims"]["all_assets_archived"] = True
    with pytest.raises(ValueError, match="claims must remain false"):
        validate_cursor(cursor)

    cursor = json.loads(
        (ROOT / "manifests/classifications/mondo-archive-cursor-2026-08-16.json").read_text(
            encoding="utf-8"
        )
    )
    cursor["observed_archived_assets"].pop(4)
    with pytest.raises(ValueError, match="contiguous through asset 6"):
        validate_cursor(cursor)


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
