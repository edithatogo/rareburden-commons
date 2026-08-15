import copy
import json
from pathlib import Path

import pytest

from scripts.audit_hpo_history import validate

ROOT = Path(__file__).resolve().parents[1]
RELEASES = ROOT / "manifests/hpo/history-frontier-2026-08-16.json"
TRANSLATIONS = ROOT / "manifests/hpo/translations-frontier-2026-08-16.json"


def test_bounded_hpo_inventory_partitions_existing_and_missing_history() -> None:
    result = validate(RELEASES, TRANSLATIONS)
    assert result == {
        "hpo_releases": 64,
        "hpo_assets": 707,
        "historical_release_gaps": 49,
        "translation_languages": 16,
        "translation_commits_observed": 128,
    }


def test_hpo_inventory_fails_closed_on_byte_route(tmp_path: Path) -> None:
    payload = json.loads(RELEASES.read_text())
    payload = copy.deepcopy(payload)
    payload["releases"][0]["assets"][0]["archive_route"] = "public_full"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="metadata-only"):
        validate(bad, TRANSLATIONS)


def test_translation_inventory_fails_closed_without_exact_licence(tmp_path: Path) -> None:
    payload = json.loads(TRANSLATIONS.read_text())
    payload["byte_archive_route"] = "public_full"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="fail closed"):
        validate(RELEASES, bad)
