from __future__ import annotations

from pathlib import Path

from scripts.check_markdown_links import local_link_errors

ROOT = Path(__file__).resolve().parents[1]


def test_repository_markdown_links_are_valid() -> None:
    assert local_link_errors(ROOT) == []


def test_missing_local_link_is_reported(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("[missing](docs/absent.md)\n", encoding="utf-8")
    errors = local_link_errors(tmp_path)
    assert errors == ["README.md: missing link target 'docs/absent.md'"]
