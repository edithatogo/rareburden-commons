from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_track_002_owner_disposition_is_bounded_and_non_activating() -> None:
    text = (ROOT / "docs/decisions/2026-08-15-track-002-bounded-source-disposition.md").read_text()
    assert "bounded_owner_preparation" in text
    assert "No production" in text and "comprehensive claim is authorized" in text
    assert "Do not substitute World Bank data for WPP" in text
    assert "Track 007 registration" in text
