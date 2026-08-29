from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.check_track003_synthetic_execution import (
    FALSE_CLAIMS,
    Track003SyntheticExecutionError,
    _scientific_projection,
    validate,
)

ROOT = Path(__file__).resolve().parents[1]
CLOSEOUT = (
    ROOT / "manifests/demonstrators/track-003-rbc-p002-synthetic-execution-closeout-2026-08-29.yml"
)


def _document() -> dict[str, object]:
    value = yaml.safe_load(CLOSEOUT.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _closeout(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "closeout.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_current_synthetic_execution_reconstructs_exactly() -> None:
    validate(CLOSEOUT, ROOT)


def test_execution_rejects_more_than_one_persisted_output(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    document["persisted_output"]["persisted_output_count"] = 2
    with pytest.raises(Track003SyntheticExecutionError, match="persisted output boundary"):
        validate(_closeout(tmp_path, document), ROOT)


@pytest.mark.parametrize("claim", sorted(FALSE_CLAIMS))
def test_execution_rejects_every_activation_or_authority_claim(tmp_path: Path, claim: str) -> None:
    document = copy.deepcopy(_document())
    document["claims"][claim] = True
    with pytest.raises(Track003SyntheticExecutionError, match="activation or authority"):
        validate(_closeout(tmp_path, document), ROOT)


def test_execution_rejects_output_hash_drift(tmp_path: Path) -> None:
    document = copy.deepcopy(_document())
    document["persisted_output"]["sha256"] = "0" * 64
    with pytest.raises(Track003SyntheticExecutionError, match="binding drift"):
        validate(_closeout(tmp_path, document), ROOT)


def test_scientific_projection_excludes_only_runtime_identity() -> None:
    result = yaml.safe_load(
        (
            ROOT / "manifests/demonstrators/track-003-rbc-p002-synthetic-execution-2026-08-29.json"
        ).read_text(encoding="utf-8")
    )
    projection = _scientific_projection(result)
    assert "runtime" not in projection
    assert "analysis_result_id" not in projection
    assert projection["summary"] == result["summary"]
    assert projection["limitations"] == result["limitations"]
    assert projection["activation_state"] == "not_activated"
