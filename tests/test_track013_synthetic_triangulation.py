import pytest

from rareburden.quality import (
    QualityAssessmentError,
    assess_synthetic_sensitivity,
    run_synthetic_model_sensitivity,
    triangulate_synthetic_estimates,
)


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


def test_synthetic_sensitivity_reports_parameter_changes_without_empirical_claims() -> None:
    result = assess_synthetic_sensitivity(
        {"source_id": "primary-synthetic", "estimate": 100},
        [{"scenario_id": "higher-missingness", "parameter": "missingness", "estimate": 120}],
    )
    assert result["intended_use"] == "synthetic_assurance"
    assert result["scenarios"][0]["relative_change"] == 0.2
    assert "not empirical evidence" in result["interpretation"]


def test_synthetic_sensitivity_requires_named_parameters() -> None:
    with pytest.raises(QualityAssessmentError, match="parameter"):
        assess_synthetic_sensitivity({"source_id": "primary", "estimate": 1}, [{"estimate": 2}])


def test_model_sensitivity_executes_each_parameter_change() -> None:
    calls = []

    def model(parameters):
        calls.append(dict(parameters))
        return parameters["population"] * parameters["fraction"]

    result = run_synthetic_model_sensitivity(
        model,
        {"population": 100, "fraction": 0.2},
        {"population": [200], "fraction": [0.1, 0.3]},
        model_id="invented-product",
    )
    assert calls == [
        {"population": 100, "fraction": 0.2},
        {"population": 200, "fraction": 0.2},
        {"population": 100, "fraction": 0.1},
        {"population": 100, "fraction": 0.3},
    ]
    assert [row["estimate"] for row in result["comparison"]["scenarios"]] == [40, 10, 30]


@pytest.mark.parametrize("value", [0, 1, 1e308])
def test_zero_baseline_has_no_relative_change(value: float) -> None:
    result = assess_synthetic_sensitivity(
        {"source_id": "zero", "estimate": 0},
        [{"parameter": "fraction", "estimate": value}],
    )
    assert result["scenarios"][0]["relative_change"] is None
    result = triangulate_synthetic_estimates(
        {"source_id": "zero", "estimate": 0},
        [{"source_id": "comparison", "estimate": value}],
        tolerance=0.1,
    )
    assert result["comparisons"][0]["within_declared_tolerance"] is None


def test_nan_tolerance_is_rejected() -> None:
    with pytest.raises(QualityAssessmentError):
        triangulate_synthetic_estimates(
            {"source_id": "baseline", "estimate": 1}, [], tolerance=float("nan")
        )
