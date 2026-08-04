from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_track_007_osf_decision_is_explicitly_unregistered() -> None:
    packet = yaml.safe_load(
        (ROOT / "docs/track-007-registration-challenge-readiness-2026-08-04.yml").read_text()
    )
    assert packet["submission_readiness"]["selected_registry"] == "osf"
    assert packet["submission_readiness"]["fallback_registry"] == "zenodo"
    assert packet["submission_readiness"]["status"] == "blocked_missing_authenticated_route"
    assert packet["submission_readiness"]["decision_record"].startswith("docs/decisions/")
