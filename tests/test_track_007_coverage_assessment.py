from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
ASSESSMENT = ROOT / "docs/track-007-coverage-language-geography-community-2026-08-20.yml"


def test_coverage_assessment_is_fail_closed() -> None:
    data = yaml.safe_load(ASSESSMENT.read_text(encoding="utf-8"))
    assert data["protocol"]["status"] == "supplemental_non_freezing_addendum"
    assert data["observed_coverage"]["crossref_expansion"]["record_language_missing"] == 480
    assert data["observed_coverage"]["crossref_expansion"]["geography_missing"] == 480
    assert data["observed_coverage"]["community_authority"]["evidence_records"] == 0
    assert data["community_authority_gate"]["state"] == "pending"
    assert data["recommendation"]["disposition"] == "narrow_and_remediate"


def test_missingness_never_becomes_absence_or_authority() -> None:
    data = yaml.safe_load(ASSESSMENT.read_text(encoding="utf-8"))
    matrix = data["missingness_matrix"]
    assert matrix["geography"]["status"] == "unmeasured"
    assert matrix["languages"]["status"] == "incomplete"
    assert matrix["community_authority"]["status"] == "pending"
    prohibited = data["community_authority_gate"]["prohibited_substitutions"]
    assert "agent-panel findings for patient/community authority" in prohibited
