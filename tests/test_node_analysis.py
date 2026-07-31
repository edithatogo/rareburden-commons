from __future__ import annotations

import pytest

from rareburden.node import run_offline_node
from rareburden.node_analysis import SyntheticAnalysisError, aggregate_synthetic_records


def test_aggregate_synthetic_records_uses_exclusive_overlap_groups() -> None:
    records = [
        {"synthetic": True, "diagnoses": ["condition-a"]},
        {"synthetic": True, "diagnoses": ["condition-a", "condition-b"]},
        {"synthetic": True, "diagnoses": ["condition-b", "condition-a", "condition-a"]},
    ]

    rows = aggregate_synthetic_records(records)

    assert rows == [
        {"diagnosis": '["condition-a","condition-b"]', "count": 2},
        {"diagnosis": '["condition-a"]', "count": 1},
    ]
    assert sum(row["count"] for row in rows) == len(records)


def test_aggregate_rows_are_suitable_for_offline_node() -> None:
    rows = aggregate_synthetic_records(
        [
            {
                "synthetic": True,
                "diagnoses": ["condition-a"],
                "jurisdiction": "synthetic-au",
                "group": "synthetic-child",
            }
        ]
        * 5,
        dimensions=("jurisdiction", "group", "diagnosis"),
    )

    result = run_offline_node(
        rows,
        execution_id="synthetic-common-analysis",
        coordinator_version="0.1.0",
        node_version="0.1.0",
        analysis_id="synthetic-common-analysis",
        policy_id="synthetic-policy",
    )

    assert result["rows"] == [
        {
            "jurisdiction": "synthetic-au",
            "group": "synthetic-child",
            "diagnosis": '["condition-a"]',
            "count_status": "released",
            "count": 5,
        }
    ]


@pytest.mark.parametrize(
    "record, message",
    [
        (
            {"synthetic": True, "diagnoses": ["condition-a"], "participant-id": "P001"},
            "identifier fields",
        ),
        (
            {"synthetic": True, "diagnoses": ["condition-a"], "age": 42},
            "unknown fields",
        ),
        (
            {"synthetic": False, "diagnoses": ["condition-a"]},
            "explicitly marked synthetic",
        ),
    ],
)
def test_aggregate_synthetic_records_rejects_unbounded_inputs(
    record: dict[str, object], message: str
) -> None:
    with pytest.raises(SyntheticAnalysisError, match=message):
        aggregate_synthetic_records([record])


def test_aggregate_synthetic_records_rejects_unknown_dimensions() -> None:
    with pytest.raises(SyntheticAnalysisError, match="unknown aggregate dimensions"):
        aggregate_synthetic_records([], dimensions=("age",))


def test_diagnosis_combination_labels_cannot_collide() -> None:
    rows = aggregate_synthetic_records(
        [
            {"synthetic": True, "diagnoses": ["a+b"]},
            {"synthetic": True, "diagnoses": ["a", "b"]},
        ]
    )
    assert len(rows) == 2
    assert sum(row["count"] for row in rows) == 2


@pytest.mark.parametrize(
    "records, dimensions",
    [
        ([None], ("diagnosis",)),
        ([], (1,)),
        ([], "diagnosis"),
    ],
)
def test_malformed_containers_fail_with_bounded_error(records: object, dimensions: object) -> None:
    with pytest.raises(SyntheticAnalysisError):
        aggregate_synthetic_records(records, dimensions=dimensions)  # type: ignore[arg-type]


@pytest.mark.parametrize("diagnoses", [[], "condition-a", [""]])
def test_aggregate_synthetic_records_rejects_invalid_diagnoses(diagnoses: object) -> None:
    with pytest.raises(SyntheticAnalysisError, match="diagnoses"):
        aggregate_synthetic_records([{"synthetic": True, "diagnoses": diagnoses}])
