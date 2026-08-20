import copy
import json
from pathlib import Path

import pytest

from scripts.archive_hpo_core_frontier import archive_batch, load_candidates, staging_path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "manifests/hpo/asset-rights-matrix-2026-08-16.json"


def test_rights_matrix_is_per_asset_and_fail_closed_by_class() -> None:
    payload = json.loads(MATRIX.read_text())
    assert len(payload["assets"]) == 707
    grouped: dict[str, list[dict]] = {}
    for item in payload["assets"]:
        grouped.setdefault(item["asset_class"], []).append(item)
    assert {key: len(value) for key, value in grouped.items()} == {
        "annotations_and_mappings": 145,
        "build_reports": 31,
        "merged_imports": 96,
        "ontology_core": 288,
        "translations": 147,
    }
    assert all(item["archive_route"] == "metadata_only" for item in grouped["translations"])
    assert all(
        item["archive_route"] == "metadata_only"
        for item in grouped["annotations_and_mappings"] + grouped["merged_imports"]
    )
    assert len(load_candidates(MATRIX)) == 288


def test_public_candidate_requires_official_host_and_conditions(tmp_path: Path) -> None:
    payload = json.loads(MATRIX.read_text())
    payload = copy.deepcopy(payload)
    candidate = next(item for item in payload["assets"] if item["asset_class"] == "ontology_core")
    candidate["browser_download_url"] = "https://example.test/hp.obo"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="official GitHub"):
        load_candidates(bad)

    candidate["browser_download_url"] = "https://github.com/obophenotype/example"
    candidate["conditions"] = []
    bad.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="licence conditions"):
        load_candidates(bad)


def test_hpo_archive_uses_one_atomic_commit_per_batch() -> None:
    source = Path(archive_batch.__code__.co_filename).read_text(encoding="utf-8")
    assert source.count("api.create_commit(") == 1
    assert "api.upload_file(" not in source
    assert '"commit_mode": "single_atomic_batch_commit"' in source


def test_hpo_atomic_staging_paths_include_release_tag(tmp_path: Path) -> None:
    first = {"release_tag": "v2025-09-01", "name": "hp.owl"}
    second = {"release_tag": "v2025-10-01", "name": "hp.owl"}
    assert staging_path(tmp_path, first) != staging_path(tmp_path, second)
    assert staging_path(tmp_path, first) == tmp_path / "v2025-09-01" / "hp.owl"

    with pytest.raises(ValueError, match="plain path components"):
        staging_path(tmp_path, {"release_tag": "../escape", "name": "hp.owl"})
    with pytest.raises(ValueError, match="plain path components"):
        staging_path(tmp_path, {"release_tag": "v2025-09-01", "name": "../hp.owl"})
