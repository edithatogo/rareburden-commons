from __future__ import annotations

from pathlib import Path

from scripts.check_repository_safety import _filesystem_files, repository_files

ROOT = Path(__file__).resolve().parents[1]


def test_raw_data_directories_contain_only_notices() -> None:
    for directory in ("raw", "interim", "processed"):
        files = [path.name for path in (ROOT / "data" / directory).iterdir() if path.is_file()]
        assert files == ["README.md"]


def test_repository_file_listing_is_nonempty() -> None:
    files, mode = repository_files()
    assert files
    assert mode in {"tracked", "source-archive"}
    assert Path("README.md") in files


def test_source_archive_fallback_excludes_git_and_caches() -> None:
    files = _filesystem_files()
    assert Path("README.md") in files
    assert not any(".git" in path.parts for path in files)
    assert not any(".pytest_cache" in path.parts for path in files)
