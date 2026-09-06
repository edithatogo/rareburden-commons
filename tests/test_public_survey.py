"""Invented examples only; never challenge disclosure controls with real NHANES."""

import copy
import hashlib
import json
import math

import pytest

from rareburden.node import NodeExportError
from rareburden.node_policy_store import DurableNodePolicyStore, NodePolicyStoreError
from rareburden.public_survey import run_public_survey


def inputs():
    # Two strata, two PSUs each, five equal copies per unit; all numbers invented.
    # Case weighted totals 5*(1+3)=20; denominator 5*(1+2+3+4)=50.
    demo, diq = [], []
    for index, (h, psu, weight, code) in enumerate(
        [(1, 1, 1, 1), (1, 2, 2, 2), (2, 1, 3, 1), (2, 2, 4, 3)]
    ):
        for repeat in range(5):
            key = index * 5 + repeat + 1
            demo.append(
                {"SEQN": key, "RIDAGEYR": 20, "WTINT2YR": weight, "SDMVSTRA": h, "SDMVPSU": psu}
            )
            diq.append({"SEQN": key, "DIQ010": code})
    return demo, diq


@pytest.fixture
def runtime(tmp_path):
    with DurableNodePolicyStore(tmp_path / "survey.sqlite3") as store:
        receipt = store.register_policy(
            {
                "schema_version": "0.1.0",
                "policy_id": "survey-policy",
                "minimum_cell_count": 5,
                "max_queries_per_overlap_group": 1,
                "allowed_dimension_fields": ["group"],
                "participant_fields": ["person_id"],
                "export_mode": "aggregate_only",
            },
            recorded_at="2026-09-06T00:00:00Z",
        )
        yield {
            "store": store,
            "policy_id": receipt.policy_id,
            "policy_sha256": receipt.content_sha256,
            "demo_sha256": "a" * 64,
            "diq_sha256": "b" * 64,
            "recorded_at": "2026-09-06T00:01:00Z",
        }


def test_hand_calculated_ratio_and_variance(runtime):
    result = run_public_survey(*inputs(), **runtime)
    assert result["estimate"] == pytest.approx(0.4)
    # Normalized PSU residuals .06,-.08,.18,-.16; variance .14²+.34²=.1352.
    assert result["standard_error"] == pytest.approx(math.sqrt(0.1352))
    assert result["confidence_interval"] is None
    assert result["reliability_assessment"] == "not_completed"
    assert result["status"] == "eligible_for_local_export"
    assert result["population_release_approved"] is False
    assert result["denominator_codes"] == [1, 2, 3]
    assert result["borderline_handling"] == "noncase"
    assert result["software_agreement"] == "unverified"
    assert result["case_definition"] == "DIQ010_1"
    assert result["excluded_response_codes"] == [7, 9, "missing"]
    assert result["age_handling"] == "known_age_at_least_20_no_imputation"
    assert result["pregnancy_exception"] == (
        "question_excludes_pregnancy_only_diabetes_for_women_20plus"
    )
    assert result["proxy_responses"] == "possible"
    assert result["standardization"] == "crude_not_age_standardized"
    assert result["nonresponse_limitation"] == "complete_response_bias_not_adjusted"
    assert not any(key in result for key in ("SEQN", "rows", "counts", "denominator", "psus"))
    digest = result.pop("output_sha256")
    assert (
        digest
        == hashlib.sha256(
            json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        ).hexdigest()
    )
    with pytest.raises((NodeExportError, NodePolicyStoreError)):
        run_public_survey(*inputs(), **runtime)


def test_domain_retains_psu_with_only_infants(runtime):
    demo, diq = inputs()
    for row in demo[5:10]:
        row["RIDAGEYR"] = 0
    diq = [row for row in diq if row["SEQN"] not in range(6, 11)]
    result = run_public_survey(demo, diq, **runtime)
    # Remaining denominator40, case20: residual PSU totals .0625,0,.1875,-.25.
    assert result["estimate"] == pytest.approx(0.5)
    assert result["standard_error"] ** 2 == pytest.approx(0.0625**2 + 0.4375**2)


@pytest.mark.parametrize("code", [None, float("nan"), 7, 9])
def test_excluded_responses_remain_in_design(runtime, code):
    demo, diq = inputs()
    for row in diq[5:10]:
        row["DIQ010"] = code
    result = run_public_survey(demo, diq, **runtime)
    assert result["estimate"] == pytest.approx(0.5)
    assert result["standard_error"] ** 2 == pytest.approx(0.0625**2 + 0.4375**2)


def test_whole_estimate_suppression(runtime):
    demo, diq = inputs()
    for row in diq:
        row["DIQ010"] = 2
    result = run_public_survey(demo, diq, **runtime)
    assert result["status"] == "suppressed"
    assert result["estimate"] is result["standard_error"] is None
    assert runtime["store"].verify() == (1, 1)


@pytest.mark.parametrize(
    "field,value",
    [
        ("SEQN", True),
        ("SEQN", 1.5),
        ("SEQN", 10**500),
        ("SEQN", 2**53 + 1),
        ("WTINT2YR", -1),
        ("WTINT2YR", None),
        ("WTINT2YR", float("nan")),
        ("WTINT2YR", float("inf")),
        ("WTINT2YR", "1"),
        ("SDMVSTRA", None),
        ("SDMVSTRA", 0),
        ("SDMVPSU", 3),
        ("RIDAGEYR", -1),
        ("RIDAGEYR", 81),
        ("RIDAGEYR", 20.5),
        ("RIDAGEYR", float("inf")),
    ],
)
def test_invalid_demographics_fail_before_reservation(runtime, field, value):
    demo, diq = inputs()
    demo[0][field] = value
    with pytest.raises(NodeExportError):
        run_public_survey(demo, diq, **runtime)
    assert runtime["store"].verify() == (1, 0)


@pytest.mark.parametrize(
    "mutation",
    [
        "duplicate_demo",
        "duplicate_diq",
        "missing_join",
        "orphan",
        "missing_field",
        "invalid_code",
        "singleton",
    ],
)
def test_join_and_design_validation(runtime, mutation):
    demo, diq = inputs()
    if mutation == "duplicate_demo":
        demo.append(copy.copy(demo[0]))
    elif mutation == "duplicate_diq":
        diq.append(copy.copy(diq[0]))
    elif mutation == "missing_join":
        diq.pop()
    elif mutation == "orphan":
        diq.append({"SEQN": 100, "DIQ010": 1})
    elif mutation == "missing_field":
        del demo[0]["WTINT2YR"]
    elif mutation == "invalid_code":
        diq[0]["DIQ010"] = 4
    else:
        for row in demo:
            row["SDMVPSU"] = 1
    with pytest.raises(NodeExportError):
        run_public_survey(demo, diq, **runtime)
    assert runtime["store"].verify() == (1, 0)


def test_estimation_failure_spends_reservation(runtime, monkeypatch):
    def fail(records):
        assert runtime["store"].verify() == (1, 1)
        raise NodeExportError("injected failure")

    monkeypatch.setattr("rareburden.public_survey._estimate", fail)
    with pytest.raises(NodeExportError, match="injected"):
        run_public_survey(*inputs(), **runtime)
    with pytest.raises((NodeExportError, NodePolicyStoreError)):
        run_public_survey(*inputs(), **runtime)


def test_wrong_policy_does_not_compute(runtime, monkeypatch):
    monkeypatch.setattr("rareburden.public_survey._estimate", lambda _: pytest.fail("computed"))
    runtime["policy_sha256"] = "c" * 64
    with pytest.raises(NodePolicyStoreError):
        run_public_survey(*inputs(), **runtime)
    assert runtime["store"].verify() == (1, 0)


def test_weight_rescaling_and_zero_weight_exclusion(runtime):
    demo, diq = inputs()
    for row in demo:
        row["WTINT2YR"] *= 1e300
    demo.append({"SEQN": 100, "RIDAGEYR": 30, "WTINT2YR": 0, "SDMVSTRA": 99, "SDMVPSU": 1})
    diq.append({"SEQN": 100, "DIQ010": 1})
    result = run_public_survey(demo, diq, **runtime)
    assert result["estimate"] == pytest.approx(0.4)
    assert result["standard_error"] ** 2 == pytest.approx(0.1352)


@pytest.mark.parametrize("age", [None, float("nan")])
@pytest.mark.parametrize("has_join", [True, False])
def test_unknown_age_excluded_but_full_design_retained(runtime, age, has_join):
    demo, diq = inputs()
    for row in demo[5:10]:
        row["RIDAGEYR"] = age
    if not has_join:
        diq = [row for row in diq if row["SEQN"] not in range(6, 11)]
    result = run_public_survey(demo, diq, **runtime)
    assert result["estimate"] == pytest.approx(0.5)
    assert result["standard_error"] ** 2 == pytest.approx(0.0625**2 + 0.4375**2)


def test_all_unknown_age_suppresses_without_inference(runtime):
    demo, diq = inputs()
    for row in demo:
        row["RIDAGEYR"] = None
    result = run_public_survey(demo, diq, **runtime)
    assert result["status"] == "suppressed"
    assert result["estimate"] is result["standard_error"] is None


@pytest.mark.parametrize("age", [0.5, 1e-79])
def test_fractional_infant_age_retains_design_without_rounding(runtime, age):
    demo, diq = inputs()
    for row in demo[5:10]:
        row["RIDAGEYR"] = age
    diq = [row for row in diq if row["SEQN"] not in range(6, 11)]
    result = run_public_survey(demo, diq, **runtime)
    assert result["estimate"] == pytest.approx(0.5)
    assert result["standard_error"] ** 2 == pytest.approx(0.0625**2 + 0.4375**2)
