from __future__ import annotations

import json
from pathlib import Path

from scripts.archive_uts_current_set import plan_current_set


def test_current_set_covers_all_families_and_skips_only_artifact_plus_receipt(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "families": [
                    {
                        "release_type": "umls-full-release",
                        "releases": [
                            {
                                "fileName": "umls-2026AA-full.zip",
                                "releaseVersion": "2026AA",
                                "releaseDate": "2026-05-03",
                                "downloadUrl": "https://download.nlm.nih.gov/umls/kss/2026AA/umls-2026AA-full.zip",
                                "releaseType": "UMLS Full Release",
                                "product": "UMLS",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    artifact = "licensed-private/uts/umls-full-release/2026AA/umls-2026AA-full.zip"
    receipt = "manifests/uts/receipts/umls-full-release/00000-00000.json"
    assert not plan_current_set(manifest, {artifact})[0]["already_archived"]
    assert plan_current_set(manifest, {artifact, receipt})[0]["already_archived"]


def test_checked_in_current_set_has_all_fourteen_release_families():
    plan = plan_current_set(Path("manifests/uts/all-release-families-2026-08-15.json"), set())
    assert len(plan) == 14
    assert len({item["release_type"] for item in plan}) == 14
