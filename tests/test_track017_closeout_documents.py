from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bounded_closeout_documents_exist_and_remain_non_authorizing() -> None:
    paths = [
        ROOT / "docs/track-017-v1-changelog.md",
        ROOT / "docs/track-017-v1-migration-guide.md",
        ROOT / "docs/track-017-v1-release-notes.md",
        ROOT / "docs/track-017-exact-candidate-evidence-index.md",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "Track 017" in text
        assert "stable" in text.lower()
        assert "pending" in text.lower()
    assert "No stable tag" in (paths[2]).read_text(encoding="utf-8")
    assert "exact commit" in (paths[3]).read_text(encoding="utf-8")
