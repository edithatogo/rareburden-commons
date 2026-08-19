#!/usr/bin/env python3
"""Capture a bounded ontology-portal inventory without downloading ontology bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

OLS_ENDPOINT = "https://www.ebi.ac.uk/ols4/api/ontologies"
ALLOWED_HOSTS = {"www.ebi.ac.uk"}
MAX_RESPONSE_BYTES = 8_000_000
MAX_PAGE_SIZE = 500
USER_AGENT = "rareburden-ontology-metadata/1"


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return ""
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, parsed.query, "")
    )


def fetch(url: str, *, max_bytes: int = MAX_RESPONSE_BYTES) -> bytes:
    """Fetch one allow-listed metadata response under a hard byte ceiling."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("metadata URL is not an allow-listed HTTPS endpoint")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > max_bytes:
            raise ValueError("metadata response exceeds byte budget")
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("metadata response exceeds byte budget")
    return data


def parse_ols_page(data: bytes) -> tuple[list[dict[str, Any]], int, int]:
    """Return canonical-source records and zero-based page coordinates."""
    payload = json.loads(data)
    if not isinstance(payload, dict):
        raise ValueError("OLS response must be an object")
    embedded = payload.get("_embedded", {})
    ontologies = embedded.get("ontologies", []) if isinstance(embedded, dict) else []
    page = payload.get("page", {})
    if not isinstance(ontologies, list) or not isinstance(page, dict):
        raise ValueError("OLS response is missing pagination or ontologies")
    number = page.get("number")
    total_pages = page.get("totalPages")
    if not isinstance(number, int) or not isinstance(total_pages, int) or total_pages < 0:
        raise ValueError("OLS pagination is invalid")
    records: list[dict[str, Any]] = []
    for item in ontologies:
        if not isinstance(item, dict) or not item.get("ontologyId"):
            continue
        config = item.get("config") if isinstance(item.get("config"), dict) else {}
        annotations = item.get("annotations") if isinstance(item.get("annotations"), dict) else {}
        location = _canonical_url(str(config.get("fileLocation") or item.get("fileLocation") or ""))
        version = str(item.get("version") or config.get("version") or "unknown")
        records.append(
            {
                "portal_id": str(item["ontologyId"]),
                "version": version,
                "canonical_source_url": location or None,
                "canonical_identity": f"{location or 'unresolved'}|{version}",
                "license_annotations": annotations.get("license", []),
                "rights_annotations": annotations.get("rights", []),
                "byte_action": "disabled_pending_canonical_source_rights",
            }
        )
    ordered = sorted(
        records, key=lambda record: (record["canonical_identity"], record["portal_id"])
    )
    return ordered, number, total_pages


def build_frontier(
    *,
    observed_at: str,
    loader: Callable[[str], bytes] = fetch,
    max_pages: int = 2,
    delay_seconds: float = 2.0,
) -> dict[str, Any]:
    """Build a deterministic, bounded OLS inventory with source-level deduplication."""
    if max_pages < 1 or max_pages > 10:
        raise ValueError("max_pages must be between 1 and 10")
    if delay_seconds < 0:
        raise ValueError("delay_seconds cannot be negative")
    observations: list[dict[str, Any]] = []
    all_records: list[dict[str, Any]] = []
    total_pages: int | None = None
    for page_number in range(max_pages):
        if page_number and delay_seconds:
            time.sleep(delay_seconds)
        url = f"{OLS_ENDPOINT}?page={page_number}&size={MAX_PAGE_SIZE}"
        data = loader(url)
        records, returned_page, returned_total = parse_ols_page(data)
        if returned_page != page_number:
            raise ValueError("OLS returned an unexpected page")
        total_pages = returned_total
        observations.append({"url": url, "sha256": _digest(data), "record_count": len(records)})
        all_records.extend(records)
        if returned_page + 1 >= returned_total:
            break
    deduplicated: dict[str, dict[str, Any]] = {}
    duplicate_ids: dict[str, list[str]] = {}
    for record in all_records:
        identity = record["canonical_identity"]
        duplicate_ids.setdefault(identity, []).append(record["portal_id"])
        deduplicated.setdefault(identity, record)
    records = []
    for identity, record in sorted(deduplicated.items()):
        records.append({**record, "portal_aliases": sorted(set(duplicate_ids[identity]))})
    exhausted = total_pages is not None and len(observations) >= total_pages
    stable = {
        "schema_version": "1.0",
        "status": "bounded_metadata_only_frontier",
        "observed_at": observed_at,
        "portal": "ebi_ols4",
        "budgets": {
            "max_pages": max_pages,
            "page_size": MAX_PAGE_SIZE,
            "max_response_bytes": MAX_RESPONSE_BYTES,
            "minimum_delay_seconds": delay_seconds,
            "sequential": True,
        },
        "observations": observations,
        "canonical_records": records,
        "exhausted_within_budget": exhausted,
        "deduplication_key": "canonical_source_url_plus_upstream_version",
        "claims": {
            "ontology_bytes_downloaded": False,
            "redistribution_rights_inferred": False,
            "portal_completeness": False,
            "canonical_source_completeness": False,
        },
    }
    canonical = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    return {**stable, "frontier_sha256": _digest(canonical)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    args = parser.parse_args()
    if args.delay_seconds < 1:
        raise ValueError("live discovery delay must be at least one second")
    result = build_frontier(
        observed_at=args.observed_at,
        max_pages=args.max_pages,
        delay_seconds=args.delay_seconds,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
