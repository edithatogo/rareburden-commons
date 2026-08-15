from __future__ import annotations

import json
import urllib.parse
from pathlib import Path

import pytest

from scripts.discover_ontology_portal_frontier import build_frontier, fetch, parse_ols_page

ROOT = Path(__file__).resolve().parents[1]


def _ols_page(page: int, total_pages: int = 2) -> bytes:
    records = [
        {
            "ontologyId": f"alias-{page}",
            "version": "v1",
            "config": {"fileLocation": "https://publisher.example/ontology.owl#fragment"},
            "annotations": {"license": ["CC-BY-4.0"], "rights": ["attribute publisher"]},
        },
        {
            "ontologyId": f"unique-{page}",
            "version": f"v{page}",
            "config": {"fileLocation": f"https://publisher.example/{page}.owl"},
            "annotations": {},
        },
    ]
    return json.dumps(
        {
            "_embedded": {"ontologies": records},
            "page": {"number": page, "totalPages": total_pages},
        }
    ).encode()


def _loader(url: str) -> bytes:
    page = int(urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)["page"][0])
    return _ols_page(page)


def test_ols_frontier_is_deterministic_bounded_and_metadata_only() -> None:
    first = build_frontier(
        observed_at="2026-08-16T00:00:00Z", loader=_loader, max_pages=2, delay_seconds=0
    )
    second = build_frontier(
        observed_at="2026-08-16T00:00:00Z", loader=_loader, max_pages=2, delay_seconds=0
    )
    assert first == second
    assert first["exhausted_within_budget"] is True
    assert len(first["canonical_records"]) == 3
    aliases = next(item for item in first["canonical_records"] if len(item["portal_aliases"]) == 2)
    assert aliases["portal_aliases"] == ["alias-0", "alias-1"]
    assert aliases["canonical_source_url"] == "https://publisher.example/ontology.owl"
    assert not any(first["claims"].values())
    assert len(first["frontier_sha256"]) == 64


def test_ols_parser_rejects_malformed_pagination() -> None:
    with pytest.raises(ValueError, match="pagination"):
        parse_ols_page(json.dumps({"_embedded": {"ontologies": []}, "page": {}}).encode())


def test_ols_budget_and_fetch_host_fail_closed() -> None:
    with pytest.raises(ValueError, match="between 1 and 10"):
        build_frontier(observed_at="x", loader=_loader, max_pages=0, delay_seconds=0)
    with pytest.raises(ValueError, match="allow-listed"):
        fetch("https://example.org/ontologies")


def test_static_portal_routing_has_no_ambiguous_byte_action() -> None:
    path = ROOT / "manifests/classifications/ontology-portal-frontier-2026-08-16.json"
    manifest = json.loads(path.read_text())
    assert {record["id"] for record in manifest["records"]} == {
        "bioportal-cdo",
        "bioportal-tara",
        "bioportal-ocmr",
        "bioportal-tcdo",
        "ebi-ols4",
        "hetop",
        "globalhealthinformatics-hetop-article",
    }
    assert not any(manifest["claims"].values())
    assert all(
        record["byte_action"] in {"disabled", "metadata_workflow_only"}
        for record in manifest["records"]
    )
    ocmr = next(record for record in manifest["records"] if record["id"] == "bioportal-ocmr")
    assert ocmr["byte_action"] == "disabled"
    assert "component" in ocmr["component_risk"]


def test_docs_do_not_upgrade_portals_to_dataset_or_rights_authority() -> None:
    text = (ROOT / "docs/track-002-ontology-portal-frontier-2026-08-16.md").read_text()
    assert "visibility is not treated as a redistribution grant" in text
    assert "not a dataset" in text
    assert "No ontology file is fetched" in text
