#!/usr/bin/env python3
"""Extend public terminology history discovery under explicit request budgets."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
from collections.abc import Callable
from pathlib import Path
from typing import Any

if __package__:
    from scripts.discover_public_archive_history import _HREF, MAX_RESPONSE_BYTES, fetch
else:
    from discover_public_archive_history import _HREF, MAX_RESPONSE_BYTES, fetch

MONDO_API = "https://api.github.com/repos/monarch-initiative/mondo/releases"
CLINVAR_SURFACES = (
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/",
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/archive/",
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/archive/",
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/archive_2.0/",
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/archive_2.0/",
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/document_archives/",
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/release_notes/",
)
ORPHANET_MEDIA = (
    ("orphadata-media", "https://sciences.orphadata.com/wp-json/wp/v2/media"),
    ("orphacode-media", "https://www.orphacode.org/wp-json/wp/v2/media"),
)
ALLOWED_CLINVAR_SUFFIXES = (
    ".gz",
    ".md5",
    ".sha256",
    ".tbi",
    ".txt",
    ".xml",
    ".vcf",
    ".json",
)


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))


def parse_mondo_page(data: bytes) -> list[dict[str, Any]]:
    releases = json.loads(data)
    if not isinstance(releases, list):
        raise ValueError("MONDO response must be a list")
    records = []
    for release in releases:
        if not isinstance(release, dict) or not release.get("tag_name"):
            continue
        html_url = release.get("html_url", "")
        if urllib.parse.urlsplit(html_url).hostname != "github.com":
            raise ValueError("MONDO release has a non-GitHub release URL")
        assets = []
        for asset in release.get("assets", []):
            asset_url = asset.get("browser_download_url", "")
            if urllib.parse.urlsplit(asset_url).hostname != "github.com":
                raise ValueError("MONDO release has a non-GitHub asset URL")
            assets.append(
                {
                    "name": asset.get("name"),
                    "bytes": asset.get("size"),
                    "source_url": asset_url,
                    "byte_route": "public_CC_BY_4_0_after_exact_digest_dedup",
                }
            )
        records.append(
            {
                "release_key": release["tag_name"],
                "published_at": release.get("published_at"),
                "source_url": html_url,
                "assets": sorted(assets, key=lambda item: str(item["name"])),
                "terms_state": "repository_CC_BY_4_0_release_assets",
            }
        )
    return records


def parse_clinvar_index(page_url: str, data: bytes) -> list[dict[str, str]]:
    prefix = urllib.parse.urlsplit(page_url).path
    records: list[dict[str, str]] = []
    for value in _HREF.findall(data.decode(errors="replace")):
        url = _canonical(urllib.parse.urljoin(page_url, value))
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != "ftp.ncbi.nlm.nih.gov":
            continue
        if not parsed.path.startswith(prefix) or parsed.path == prefix:
            continue
        is_directory = parsed.path.endswith("/")
        if not is_directory and not parsed.path.lower().endswith(ALLOWED_CLINVAR_SUFFIXES):
            continue
        records.append(
            {
                "release_key": Path(parsed.path.rstrip("/")).name,
                "kind": "directory" if is_directory else "checksum_or_product",
                "source_url": url,
                "byte_route": "metadata_only_submitter_provenance_review",
                "terms_state": "official_download_route_observed_reuse_not_inferred",
            }
        )
    return sorted(
        {record["source_url"]: record for record in records}.values(), key=lambda x: x["source_url"]
    )


def parse_orphanet_media(data: bytes, *, expected_host: str) -> list[dict[str, Any]]:
    media = json.loads(data)
    if not isinstance(media, list):
        raise ValueError("Orphanet media response must be a list")
    records = []
    for item in media:
        if not isinstance(item, dict) or not item.get("source_url"):
            continue
        source_url = item["source_url"]
        if urllib.parse.urlsplit(source_url).hostname != expected_host:
            raise ValueError("Orphanet media has an unexpected source host")
        records.append(
            {
                "media_id": item.get("id"),
                "published_at": item.get("date_gmt"),
                "modified_at": item.get("modified_gmt"),
                "media_type": item.get("mime_type"),
                "source_url": source_url,
                "byte_route": "metadata_only_until_exact_file_terms_and_digest_dedup",
                "terms_state": "official_media_metadata_observed_rights_not_inferred",
            }
        )
    return records


def build_frontier(
    *,
    observed_at: str,
    loader: Callable[[str], bytes] = fetch,
    delay_seconds: float = 1.0,
    max_mondo_pages: int = 10,
    max_orphanet_pages: int = 5,
) -> dict[str, Any]:
    if max_mondo_pages < 1 or max_orphanet_pages < 1:
        raise ValueError("page budgets must be positive")
    observations: list[dict[str, Any]] = []

    def load(url: str) -> bytes:
        if observations and delay_seconds:
            time.sleep(delay_seconds)
        return loader(url)

    mondo_exhausted = False
    for page in range(1, max_mondo_pages + 1):
        url = f"{MONDO_API}?per_page=100&page={page}"
        data = load(url)
        records = parse_mondo_page(data)
        observations.append(
            {
                "family": "mondo",
                "surface_url": url,
                "surface_sha256": _hash(data),
                "records": records,
            }
        )
        if len(records) < 100:
            mondo_exhausted = True
            break

    for url in CLINVAR_SURFACES:
        data = load(url)
        observations.append(
            {
                "family": "clinvar",
                "surface_url": url,
                "surface_sha256": _hash(data),
                "records": parse_clinvar_index(url, data),
            }
        )

    orphanet_exhausted: dict[str, bool] = {}
    for family, endpoint in ORPHANET_MEDIA:
        expected_host = urllib.parse.urlsplit(endpoint).hostname
        if expected_host is None:
            raise ValueError("Orphanet endpoint has no host")
        orphanet_exhausted[family] = False
        for page in range(1, max_orphanet_pages + 1):
            url = f"{endpoint}?per_page=100&page={page}"
            data = load(url)
            records = parse_orphanet_media(data, expected_host=expected_host)
            observations.append(
                {
                    "family": family,
                    "surface_url": url,
                    "surface_sha256": _hash(data),
                    "records": records,
                }
            )
            if len(records) < 100:
                orphanet_exhausted[family] = True
                break

    observations.sort(key=lambda item: (item["family"], item["surface_url"]))
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "status": "bounded_official_history_frontier",
        "observed_at": observed_at,
        "budgets": {
            "max_mondo_pages": max_mondo_pages,
            "max_orphanet_pages_per_site": max_orphanet_pages,
            "records_per_paginated_request": 100,
            "max_response_bytes": MAX_RESPONSE_BYTES,
            "minimum_delay_seconds": delay_seconds,
            "sequential": True,
        },
        "exhaustion": {"mondo_release_api": mondo_exhausted, **orphanet_exhausted},
        "deduplication": {
            "identity": "sha256_before_byte_upload",
            "existing_manifest": (
                "manifests/classifications/public-history-products-2026-08-16.json"
            ),
            "existing_hf_receipts": "docs/track-002-terminology-archive-receipts-2026-08-16.yml",
            "equivalent_bytes_action": "reuse_existing_path_and_receipt",
        },
        "observations": observations,
        "claims": {
            "all_official_surfaces_enumerated": False,
            "historical_completeness": False,
            "language_completeness": False,
            "redistribution_rights_inferred": False,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["frontier_sha256"] = _hash(canonical)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--max-mondo-pages", type=int, default=10)
    parser.add_argument("--max-orphanet-pages", type=int, default=5)
    args = parser.parse_args()
    if args.delay_seconds < 1:
        raise ValueError("live discovery delay must be at least one second")
    payload = build_frontier(
        observed_at=args.observed_at,
        delay_seconds=args.delay_seconds,
        max_mondo_pages=args.max_mondo_pages,
        max_orphanet_pages=args.max_orphanet_pages,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
