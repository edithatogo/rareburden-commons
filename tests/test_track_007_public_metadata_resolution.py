from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "resolve_track_007_public_metadata",
    ROOT / "scripts" / "resolve_track_007_public_metadata.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_description_rule_resolves_only_explicit_contributions() -> None:
    results = {
        "records": [
            {
                "registry": "github",
                "query_string": "rare disease burden",
                "first_page_records": [
                    {
                        "identifier": "a/include",
                        "title": "Example",
                        "canonical_url": "https://example.invalid/include",
                        "description": "Rare disease burden measurement dataset",
                    },
                    {
                        "identifier": "b/pending",
                        "title": "Rare disease registry",
                        "canonical_url": "https://example.invalid/pending",
                        "description": "Demonstration project",
                    },
                ],
            }
        ]
    }
    screening = {
        "decisions": [
            {
                "canonical_key": "github:a/include",
                "decision": "include",
                "occurrences": [
                    {"registry": "github", "query_string": "rare disease burden", "rank": 1}
                ],
            },
            {
                "canonical_key": "github:b/pending",
                "decision": "include",
                "occurrences": [
                    {"registry": "github", "query_string": "rare disease burden", "rank": 2}
                ],
            },
        ]
    }
    report = MODULE.resolve(json.dumps(results).encode(), json.dumps(screening).encode())
    assert report["counts"]["include_resolutions"] == 1
    assert report["counts"]["pending"] == 1
    assert report["resolutions"][0]["canonical_key"] == "github:a/include"


def test_committed_resolutions_reconstruct_hashes_without_copying_descriptions() -> None:
    results_raw = (ROOT / "docs/track-007-search-results-2026-08-15.json").read_bytes()
    screening_raw = (ROOT / "docs/track-007-screening-2026-08-15.json").read_bytes()
    committed = json.loads(
        (ROOT / "docs/track-007-public-metadata-resolutions-2026-08-16.json").read_text()
    )
    rebuilt = MODULE.resolve(results_raw, screening_raw)
    assert committed == rebuilt
    assert committed["search_results_sha256"] == "sha256:" + hashlib.sha256(results_raw).hexdigest()
    assert committed["counts"]["include_resolutions"] > 0
    serialized = json.dumps(committed).casefold()
    assert '"description"' not in serialized
    assert '"abstract"' not in serialized
