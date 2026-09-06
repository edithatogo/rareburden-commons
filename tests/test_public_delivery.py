"""Invented aggregate-only delivery fault and recovery tests."""

import os
from pathlib import Path

import pytest

from rareburden.public_delivery import create_run_directory, recover_results, stage_results

posix_delivery = pytest.mark.skipif(
    os.name != "posix", reason="Durable public delivery is qualified only on POSIX filesystems"
)


def test_directory_sync_closes_descriptor_on_error(tmp_path, monkeypatch):
    from rareburden.public_delivery import _sync_directory

    closed = []
    monkeypatch.setattr(os, "open", lambda *args: 42)
    monkeypatch.setattr(os, "close", closed.append)

    def fail(descriptor):
        raise OSError("injected fsync failure")

    monkeypatch.setattr(os, "fsync", fail)
    with pytest.raises(OSError, match="injected"):
        _sync_directory(tmp_path)
    assert closed == [42]


def test_new_run_syncs_existing_parent(tmp_path: Path, monkeypatch) -> None:
    calls = []
    monkeypatch.setattr("rareburden.public_delivery._sync_directory", calls.append)
    output = tmp_path / "run"
    create_run_directory(output)
    assert output.is_dir()
    assert calls == [tmp_path]
    with pytest.raises(FileExistsError):
        create_run_directory(output)
    with pytest.raises(FileNotFoundError):
        create_run_directory(tmp_path / "missing" / "run")


@posix_delivery
def test_stage_and_recover_idempotently(tmp_path: Path) -> None:
    digest = stage_results(tmp_path, {"test": {"count": 10}})
    assert not (tmp_path / "results.json").exists()
    assert recover_results(tmp_path) == digest
    assert recover_results(tmp_path) == digest


def test_missing_receipt_never_publishes(tmp_path: Path) -> None:
    (tmp_path / "results.staged.json").write_text('{"count":10}')
    with pytest.raises(FileNotFoundError):
        recover_results(tmp_path)
    assert not (tmp_path / "results.json").exists()


@posix_delivery
def test_corruption_and_overwrite_rejected(tmp_path: Path) -> None:
    stage_results(tmp_path, {"count": 10})
    (tmp_path / "results.json").write_text("unrelated")
    with pytest.raises(ValueError, match="differs"):
        recover_results(tmp_path)
    (tmp_path / "results.staged.json").write_text("corrupt")
    with pytest.raises(ValueError, match="digest mismatch"):
        recover_results(tmp_path)
    assert (tmp_path / "results.json").read_text() == "unrelated"


@posix_delivery
def test_stage_is_single_use_and_rejects_nan(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        stage_results(tmp_path, {"count": float("nan")})
    stage_results(tmp_path, {"count": 10})
    with pytest.raises(FileExistsError):
        stage_results(tmp_path, {"count": 20})


@posix_delivery
def test_symlink_rejected(tmp_path: Path) -> None:
    stage_results(tmp_path, {"count": 10})
    (tmp_path / "results.json").symlink_to(tmp_path / "results.staged.json")
    with pytest.raises(ValueError, match="symbolic"):
        recover_results(tmp_path)


@posix_delivery
def test_link_failure_can_recover_without_recomputation(tmp_path: Path, monkeypatch) -> None:
    digest = stage_results(tmp_path, {"count": 10})
    real_link = os.link

    def fail(*args, **kwargs):
        raise OSError("injected delivery failure")

    monkeypatch.setattr(os, "link", fail)
    with pytest.raises(OSError, match="injected"):
        recover_results(tmp_path)
    monkeypatch.setattr(os, "link", real_link)
    assert recover_results(tmp_path) == digest
