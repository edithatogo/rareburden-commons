#!/usr/bin/env python3
"""Discover bounded official release metadata without downloading source bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

USER_AGENT = "rareburden-archive-metadata/1"
MAX_RESPONSE_BYTES = 8_000_000
DEFAULT_DELAY_SECONDS = 1.0
ORPHADATA_PAGES = (
    "alignments/",
    "classifications/",
    "linearisation/",
    "genes/",
    "phenotypes/",
    "functional-consequences/",
    "epidemiology/",
    "natural-history/",
)
SURFACES = {
    "orphacode": "https://www.orphacode.org/pack-nomenclature/",
    "mondo": "https://api.github.com/repos/monarch-initiative/mondo/releases?per_page=100",
    "clinvar": "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/archive/",
}
_HREF = re.compile(r"href=[\"']([^\"']+)[\"']", re.I)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str, *, max_bytes: int = MAX_RESPONSE_BYTES) -> bytes:
    """Fetch one official metadata surface with a hard response-size ceiling."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > max_bytes:
            raise ValueError(f"metadata response exceeds byte budget: {url}")
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"metadata response exceeds byte budget: {url}")
    return data


def _official_links(
    html: str, page_url: str, hosts: set[str], suffixes: tuple[str, ...]
) -> list[str]:
    links: list[str] = []
    for value in _HREF.findall(html):
        url = urllib.parse.urljoin(page_url, value)
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname not in hosts:
            continue
        if not parsed.path.lower().endswith(suffixes):
            continue
        canonical = urllib.parse.urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, parsed.query, "")
        )
        if canonical not in links:
            links.append(canonical)
    return links


def discover_orphacode(data: bytes) -> list[dict[str, Any]]:
    links = _official_links(
        data.decode(errors="replace"), SURFACES["orphacode"], {"www.orphacode.org"}, (".zip",)
    )
    return [
        {
            "release_key": Path(urllib.parse.urlsplit(url).path).name,
            "source_url": url,
            "byte_route": "existing_public_archive_or_digest_deduplicated_CC_BY_4_0",
            "terms_state": "CC_BY_4_0_observed_on_official_pack_page",
        }
        for url in links
    ]


def discover_orphadata(page_url: str, data: bytes) -> list[dict[str, Any]]:
    suffixes = (".xml", ".json", ".json.tar.gz", ".csv", ".zip", ".xlsx", ".txt")
    links = _official_links(
        data.decode(errors="replace"), page_url, {"www.orphadata.com"}, suffixes
    )
    return [
        {
            "release_key": Path(urllib.parse.urlsplit(url).path).name,
            "product_page": page_url,
            "source_url": url,
            "byte_route": "existing_public_archive_or_digest_deduplicated_CC_BY_4_0",
            "terms_state": "CC_BY_4_0_observed_on_official_product_page",
        }
        for url in links
    ]


def discover_mondo(data: bytes) -> list[dict[str, Any]]:
    releases = json.loads(data)
    if not isinstance(releases, list):
        raise ValueError("MONDO release response must be a list")
    result: list[dict[str, Any]] = []
    for release in releases:
        if not isinstance(release, dict) or not release.get("tag_name"):
            continue
        assets = []
        for asset in release.get("assets", []):
            url = asset.get("browser_download_url", "")
            if urllib.parse.urlsplit(url).hostname != "github.com":
                continue
            assets.append(
                {"name": asset.get("name"), "source_url": url, "bytes": asset.get("size")}
            )
        result.append(
            {
                "release_key": release["tag_name"],
                "published_at": release.get("published_at"),
                "source_url": release.get("html_url"),
                "assets": sorted(assets, key=lambda item: str(item["name"])),
                "byte_route": "public_CC_BY_4_0_after_exact_digest_dedup",
                "terms_state": "repository_CC_BY_4_0_release_assets",
            }
        )
    return sorted(result, key=lambda item: str(item["release_key"]), reverse=True)


def discover_clinvar(data: bytes) -> list[dict[str, Any]]:
    links = _official_links(
        data.decode(errors="replace"),
        SURFACES["clinvar"],
        {"ftp.ncbi.nlm.nih.gov"},
        (".gz", ".md5"),
    )
    return [
        {
            "release_key": Path(urllib.parse.urlsplit(url).path).name,
            "source_url": url,
            "byte_route": "metadata_only_submitter_provenance_review",
            "terms_state": "public_download_observed_reuse_not_inferred",
        }
        for url in links
    ]


def build_inventory(
    *,
    observed_at: str,
    loader: Callable[[str], bytes] = fetch,
    delay_seconds: float = DEFAULT_DELAY_SECONDS,
) -> dict[str, Any]:
    """Build a content-addressed, bounded inventory over enumerated official surfaces."""
    observations: list[dict[str, Any]] = []

    def observe(family: str, url: str, parser: Callable[[bytes], list[dict[str, Any]]]) -> None:
        data = loader(url)
        records = parser(data)
        observations.append(
            {
                "family": family,
                "surface_url": url,
                "surface_sha256": _sha256(data),
                "records": records,
            }
        )

    observe("orphacode", SURFACES["orphacode"], discover_orphacode)
    for slug in ORPHADATA_PAGES:
        if delay_seconds:
            time.sleep(delay_seconds)
        page_url = urllib.parse.urljoin("https://sciences.orphadata.com/", slug)
        observe("orphadata", page_url, lambda data, url=page_url: discover_orphadata(url, data))
    if delay_seconds:
        time.sleep(delay_seconds)
    observe("mondo", SURFACES["mondo"], discover_mondo)
    if delay_seconds:
        time.sleep(delay_seconds)
    observe("clinvar", SURFACES["clinvar"], discover_clinvar)

    observations.sort(key=lambda item: (item["family"], item["surface_url"]))
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "status": "bounded_official_surface_inventory",
        "observed_at": observed_at,
        "rate_policy": {
            "sequential": True,
            "minimum_delay_seconds": delay_seconds,
            "max_response_bytes": MAX_RESPONSE_BYTES,
        },
        "deduplication": {
            "identity": "sha256_before_upload",
            "existing_receipts": "docs/track-002-terminology-archive-receipts-2026-08-16.yml",
            "equivalent_bytes_action": "reuse_existing_path_and_receipt",
        },
        "observations": observations,
        "claims": {
            "historical_completeness": False,
            "language_completeness": False,
            "product_completeness": False,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["inventory_sha256"] = _sha256(canonical)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--delay-seconds", type=float, default=DEFAULT_DELAY_SECONDS)
    args = parser.parse_args()
    if args.delay_seconds < 1.0:
        raise ValueError("live discovery delay must be at least one second")
    inventory = build_inventory(observed_at=args.observed_at, delay_seconds=args.delay_seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
