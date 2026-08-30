from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from scripts.check_track003_aetiologic_evidence_qualification import (
    QualificationError,
    validate,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "track-003-aetiologic-evidence-qualification-2026-08-30.yml"


def _document() -> dict[str, object]:
    value = yaml.safe_load(ARTIFACT.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _mutate(tmp_path: Path, document: dict[str, object]) -> Path:
    path = tmp_path / "qualification.yml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_exact_qualification_is_valid() -> None:
    validate(ARTIFACT)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("empirical_activation", True),
        ("public_aggregate_execution", True),
        ("independent_review", True),
        ("publication_authority", True),
    ],
)
def test_authority_escalation_fails_closed(tmp_path: Path, field: str, value: bool) -> None:
    document = deepcopy(_document())
    document["authority_boundaries"][field] = value
    with pytest.raises(QualificationError):
        validate(_mutate(tmp_path, document))


def test_source_cannot_be_promoted_to_direct_use(tmp_path: Path) -> None:
    document = deepcopy(_document())
    document["sources"][0]["assessment"]["use_decision"] = "direct_use"
    with pytest.raises(QualificationError):
        validate(_mutate(tmp_path, document))


def test_rights_receipt_cannot_be_removed(tmp_path: Path) -> None:
    document = deepcopy(_document())
    del document["sources"][1]["licence"]
    with pytest.raises(QualificationError):
        validate(_mutate(tmp_path, document))


def test_possible_search_prodigy_overlap_cannot_be_hidden(tmp_path: Path) -> None:
    document = deepcopy(_document())
    document["coverage_assessment"]["overlap"] = "none"
    with pytest.raises(QualificationError):
        validate(_mutate(tmp_path, document))
