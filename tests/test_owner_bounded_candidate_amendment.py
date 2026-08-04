from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_owner_amendment_preserves_bounded_scope_and_expiry() -> None:
    text = (ROOT / "docs/decisions/2026-08-05-owner-bounded-candidate-amendment.md").read_text()
    assert "Peeled commit: `4b40336`" in text
    assert "Review/expiry: 2026-09-03" in text
    assert "no backup owner" in text
    assert "does not authorize production activation" in text
