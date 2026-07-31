from __future__ import annotations

from pathlib import Path

import pytest

from rareburden.schema import SchemaValidationError, load_document, load_mapping


def test_duplicate_yaml_key_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.yml"
    path.write_text("analysis_id: first\nanalysis_id: second\n", encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="duplicate key 'analysis_id'"):
        load_document(path)


def test_yaml_merge_cannot_silently_override_a_key(tmp_path: Path) -> None:
    path = tmp_path / "merge.yml"
    path.write_text(
        "defaults: &defaults\n  status: planned\nrecord:\n  <<: *defaults\n  status: active\n",
        encoding="utf-8",
    )

    with pytest.raises(SchemaValidationError, match="duplicate key 'status'"):
        load_mapping(path)


def test_safe_yaml_loader_does_not_construct_python_objects(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.yml"
    path.write_text("value: !!python/object/apply:os.system ['echo unsafe']\n", encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="Invalid document"):
        load_document(path)
