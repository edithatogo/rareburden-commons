from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "docs/decisions/2026-08-29-track-003-bounded-registration-disposition.yml"
EXPECTED_COMMIT = "675c38e6c09099878c8087f7b722cea32c4d9277"
EXPECTED_TREE = "b86f8754fcd6093c1baa6d9189c96d96d4a423e5"
EXPECTED_REGISTRATION_SHA = "fceee6bfd1ea62a4413e0e9aa9afab61a5a098a327b884ae94891b85ef7f2cec"


def _load(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_track003_bounded_review_closeout_is_exact_and_non_activating() -> None:
    decision = _load(DECISION)
    candidate = decision["candidate"]
    assert candidate["commit"] == EXPECTED_COMMIT
    assert candidate["tree"] == EXPECTED_TREE
    actual_tree = subprocess.run(
        ["git", "rev-parse", f"{EXPECTED_COMMIT}^{{tree}}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert actual_tree == EXPECTED_TREE
    registration = ROOT / candidate["registration"]
    assert hashlib.sha256(registration.read_bytes()).hexdigest() == EXPECTED_REGISTRATION_SHA
    assert candidate["registration_sha256"] == EXPECTED_REGISTRATION_SHA
    assert decision["decision"] == {
        "selected_option": "accept_bounded_interface_registration",
        "bounded_interface_registered": True,
        "track_complete": False,
        "execution_authorized": False,
        "next_work": (
            "Qualify a protocol-compatible synthetic denominator or an exact "
            "rights-receipted public-aggregate parameter set under issue 261."
        ),
    }
    claims = decision["claims"]
    assert claims["agent_panel_review_complete"] is True
    assert all(
        value is False for key, value in claims.items() if key != "agent_panel_review_complete"
    )


def test_track003_review_receipts_bind_the_same_candidate_and_preserve_authority() -> None:
    decision = _load(DECISION)
    receipts = decision["agent_review_receipts"]
    assert set(receipts) == {
        "scientific_methods",
        "engineering_reproducibility_security",
        "simulated_patient_community_harm",
    }
    for relative_path in receipts.values():
        receipt = _load(ROOT / relative_path)
        assert receipt["reviewed_candidate"] == {
            "commit": EXPECTED_COMMIT,
            "tree": EXPECTED_TREE,
            "registration_sha256": EXPECTED_REGISTRATION_SHA,
        }
        assert receipt["disposition"] == "pass_bounded_interface_registration"
        assert receipt["unresolved_blocking_findings"] == []
        authority = receipt["authority"]
        assert authority["independent_review"] is False
        assert authority["recommendation_is_approval"] is False
