import pytest

from rareburden.quality import QualityAssessmentError, triangulate_synthetic_estimates


def test_synthetic_triangulation_is_deterministic_and_non_empirical() -> None:
    result = triangulate_synthetic_estimates(
        {"source_id": "primary-synthetic", "estimate": 100},
        [
            {"source_id": "independent-fixture-a", "estimate": 105},
            {"source_id": "independent-fixture-b", "estimate": 130},
        ],
        tolerance=0.1,
    )
    assert result["intended_use"] == "synthetic_assurance"
    assert result["comparisons"][0]["within_declared_tolerance"] is True
    assert result["comparisons"][1]["within_declared_tolerance"] is False
    assert "not empirical validation" in result["interpretation"]


@pytest.mark.parametrize("tolerance", [-0.1, 1, "0.1"])
def test_synthetic_triangulation_bounds_fail_closed(tolerance: object) -> None:
    with pytest.raises(QualityAssessmentError):
        triangulate_synthetic_estimates(
            {"source_id": "primary", "estimate": 1},
            [],
            tolerance=tolerance,  # type: ignore[arg-type]
        )
