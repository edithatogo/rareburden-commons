from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.archive_mondo_release_batch import (
    DESTINATION,
    commit_asset_batch,
    mondo_releases,
    pace_source_download,
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


def test_selection_rejects_nonpublic_terms_or_byte_route() -> None:
    releases = mondo_releases(json.loads(MANIFEST.read_text(encoding="utf-8")))
    releases[0]["terms_state"] = "metadata_only"
    with pytest.raises(ValueError, match="exact public terms"):
        select_assets(releases, release_index=0, asset_start=0, asset_count=1)

    releases = mondo_releases(json.loads(MANIFEST.read_text(encoding="utf-8")))
    releases[0]["assets"][0]["byte_route"] = "restricted_no_public_bytes"
    with pytest.raises(ValueError, match="outside the public route"):
        select_assets(releases, release_index=0, asset_start=0, asset_count=1)


def test_new_assets_are_published_in_one_atomic_commit() -> None:
    calls: list[dict[str, object]] = []

    class FakeApi:
        def create_commit(self, **kwargs: object) -> None:
            calls.append(kwargs)

    operations = [object(), object(), object()]
    commit_asset_batch(FakeApi(), operations, release="v2026-01-06")
    assert calls == [
        {
            "repo_id": DESTINATION,
            "repo_type": "dataset",
            "operations": operations,
            "commit_message": "Archive bounded MONDO v2026-01-06 asset batch",
        }
    ]

    calls.clear()
    commit_asset_batch(FakeApi(), [], release="v2026-01-06")
    assert calls == []


def test_source_download_pacing_preserves_two_second_delay() -> None:
    delays: list[float] = []
    pace_source_download(0, sleeper=delays.append)
    pace_source_download(1, sleeper=delays.append)
    pace_source_download(5, sleeper=delays.append)
    assert delays == [2.0, 2.0]


def test_committed_cursor_resumes_after_hosted_batch() -> None:
    assert resolve_cursor(None, None) == (9, 0)
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
    assert len(cursor["observed_archived_assets"]) == 241
    assert sum(item["bytes"] for item in cursor["observed_archived_assets"]) == 18_084_035_696

    cursor["hosted_receipts"][-1]["asset_start"] = 29
    cursor["hosted_receipts"][-1]["asset_end"] = 29
    with pytest.raises(ValueError, match="do not exactly cover"):
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
    with pytest.raises(ValueError, match="contiguous within each release"):
        validate_cursor(cursor)

    cursor = json.loads(
        (ROOT / "manifests/classifications/mondo-archive-cursor-2026-08-16.json").read_text(
            encoding="utf-8"
        )
    )
    cursor["observed_archived_assets"] = [
        item
        for item in cursor["observed_archived_assets"]
        if item["release_index"] != 8 or item["asset_index"] < 5
    ]
    cursor["hosted_receipts"] = [
        item for item in cursor["hosted_receipts"] if item.get("release_index") != 8
    ]
    cursor["hosted_receipts"].append(
        {
            "artifact_digest_sha256": "a" * 64,
            "asset_end": 4,
            "asset_start": 0,
            "head_sha": "b" * 40,
            "receipt_sha256": "c" * 64,
            "release_index": 8,
            "run_id": 1,
        }
    )
    cursor["last_successful_run"].update(
        {
            "head_sha": "b" * 40,
            "receipt_sha256": "c" * 64,
            "run_id": 1,
        }
    )
    with pytest.raises(ValueError, match="next cursor"):
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
