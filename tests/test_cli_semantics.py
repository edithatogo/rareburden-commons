from __future__ import annotations

import json
from pathlib import Path

from rareburden.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_validate_hierarchy_cli_reports_mapping(capsys: object) -> None:
    status = main(
        [
            "validate-hierarchy",
            "--root",
            str(ROOT),
            "--hierarchy",
            "examples/semantics/rare-within-common-synthetic.yml",
            "--mapping",
            "examples/semantics/orpha-to-synthetic-mapping.yml",
            "--json",
        ]
    )
    assert status == 0
    output = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert output["entity_count"] == 6
    assert output["mapping"]["mapping_count"] == 2


def test_aggregate_hierarchy_cli_writes_valid_result(tmp_path: Path, capsys: object) -> None:
    output = tmp_path / "aggregate.json"
    status = main(
        [
            "aggregate-hierarchy",
            "--root",
            str(ROOT),
            "--hierarchy",
            "examples/semantics/rare-within-common-synthetic.yml",
            "--counts",
            "examples/semantics/monogenic-counts-synthetic.yml",
            "--output",
            str(output),
            "--json",
        ]
    )
    assert status == 0
    payload = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert payload["value"] == 55
    assert json.loads(output.read_text(encoding="utf-8"))["result_id"] == payload["result_id"]


def test_mapping_schema_without_mapping_fails(capsys: object) -> None:
    status = main(
        [
            "validate-hierarchy",
            "--root",
            str(ROOT),
            "--hierarchy",
            "examples/semantics/rare-within-common-synthetic.yml",
            "--mapping-schema",
            "schemas/ontology-mapping.schema.json",
        ]
    )
    assert status == 1
    assert "requires --mapping" in capsys.readouterr().err  # type: ignore[attr-defined]
