from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.archive_orphacode_batch import discover_pack_urls


def test_discovery_keeps_unique_official_https_zip_links_in_page_order():
    html = """
    <a href="/data/packs/Pack_EN.zip">English</a>
    <a href="https://www.orphacode.org/data/packs/Pack_FR.zip">French</a>
    <a href="/data/packs/Pack_EN.zip">duplicate</a>
    <a href="https://evil.example/Pack.zip">untrusted</a>
    """
    assert discover_pack_urls(html) == [
        "https://www.orphacode.org/data/packs/Pack_EN.zip",
        "https://www.orphacode.org/data/packs/Pack_FR.zip",
    ]


def test_discovery_fails_closed_when_no_official_pack_exists():
    with pytest.raises(ValueError, match="no official ZIP"):
        discover_pack_urls('<a href="https://example.org/not-a-pack.zip">x</a>')


def test_classification_catalog_covers_requested_systems_and_axes():
    catalog = json.loads(
        Path("manifests/classifications/archive-catalog-2026-08-15.json").read_text()
    )
    families = {item["id"]: item for item in catalog["families"]}
    assert {
        "who-icd-11",
        "who-icd-10",
        "who-historical-icd",
        "who-fic-foundation",
        "who-icf",
        "who-ichi",
        "who-fic-derived-related",
        "meddra",
        "orphacode-nomenclature-packs",
        "orphadata-scientific-files",
        "snomed-ct",
        "umls-knowledge-sources",
    } == set(families)
    for family in families.values():
        assert all(family[field] for field in ("versions", "languages", "countries"))
    assert families["meddra"]["route"] == "private_licensed_only"
    assert families["snomed-ct"]["route"] == "private_licensed_only"
    assert families["orphacode-nomenclature-packs"]["route"] == "public_exact_unmodified"
