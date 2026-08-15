#!/usr/bin/env python3
"""Recursively enumerate bounded official ClinVar metadata without source bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.parse
from collections import deque
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

if __package__:
    from scripts.discover_public_archive_frontier import CLINVAR_SURFACES, parse_clinvar_index
    from scripts.discover_public_archive_history import fetch
else:
    from discover_public_archive_frontier import CLINVAR_SURFACES, parse_clinvar_index
    from discover_public_archive_history import fetch


def discover(
    *,
    observed_at: str,
    max_requests: int,
    max_depth: int,
    delay_seconds: float,
    loader: Callable[[str], bytes] = fetch,
) -> dict:
    if max_requests < len(CLINVAR_SURFACES) or max_depth < 0:
        raise ValueError("ClinVar traversal budgets are invalid")
    queue = deque((url, 0, url) for url in CLINVAR_SURFACES)
    seen: set[str] = set()
    observations = []
    while queue and len(observations) < max_requests:
        url, depth, root = queue.popleft()
        if url in seen:
            continue
        if observations and delay_seconds:
            time.sleep(delay_seconds)
        data = None
        failure: urllib.error.URLError | None = None
        for attempt in range(3):
            try:
                data = loader(url)
                failure = None
                break
            except urllib.error.HTTPError as error:
                if error.code not in {403, 404}:
                    raise
                failure = error
                break
            except urllib.error.URLError as error:
                failure = error
                if attempt < 2 and delay_seconds:
                    time.sleep(delay_seconds)
        if data is None:
            status = failure.code if isinstance(failure, urllib.error.HTTPError) else None
            observations.append(
                {
                    "surface_url": url,
                    "root_product": root,
                    "depth": depth,
                    "http_status": status,
                    "records": [],
                    "state": "official_directory_unavailable_fail_closed",
                }
            )
            seen.add(url)
            continue
        records = parse_clinvar_index(url, data)
        for record in records:
            record["artifact_name"] = record.pop("release_key")
        observations.append(
            {
                "surface_url": url,
                "root_product": root,
                "depth": depth,
                "surface_sha256": hashlib.sha256(data).hexdigest(),
                "records": records,
            }
        )
        seen.add(url)
        if depth < max_depth and root != CLINVAR_SURFACES[0]:
            for record in records:
                child = record["source_url"]
                if record["kind"] != "directory" or child in seen:
                    continue
                parsed = urllib.parse.urlsplit(child)
                root_path = urllib.parse.urlsplit(root).path
                if parsed.hostname == "ftp.ncbi.nlm.nih.gov" and parsed.path.startswith(root_path):
                    queue.append((child, depth + 1, root))
    payload = {
        "schema_version": "1.0",
        "status": "bounded_recursive_clinvar_metadata",
        "observed_at": observed_at,
        "budgets": {
            "max_requests": max_requests,
            "max_depth": max_depth,
            "minimum_delay_seconds": delay_seconds,
            "sequential": True,
        },
        "observations": observations,
        "frontier_queue_count": len(queue),
        "exhausted_within_scope": not queue,
        "byte_route": "metadata_only_submitter_provenance_review",
        "claims": {"product_completeness": False, "redistribution_rights": False},
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["inventory_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def validate_inventory(document: dict[str, Any]) -> dict[str, int | bool]:
    """Validate a committed metadata-only ClinVar observation fail closed."""
    if document.get("status") != "bounded_recursive_clinvar_metadata":
        raise ValueError("ClinVar inventory status is invalid")
    budgets = document.get("budgets")
    if (
        not isinstance(budgets, Mapping)
        or budgets.get("sequential") is not True
        or budgets.get("max_depth") != 2
        or not isinstance(budgets.get("max_requests"), int)
        or budgets["max_requests"] < len(CLINVAR_SURFACES)
        or float(budgets.get("minimum_delay_seconds", 0)) < 1
    ):
        raise ValueError("ClinVar committed traversal budgets are invalid")
    if document.get("byte_route") != "metadata_only_submitter_provenance_review":
        raise ValueError("ClinVar inventory must remain metadata-only")
    claims = document.get("claims")
    if not isinstance(claims, Mapping) or set(claims) != {
        "product_completeness",
        "redistribution_rights",
    }:
        raise ValueError("ClinVar claims contract is invalid")
    if any(claims.values()):
        raise ValueError("ClinVar completeness and redistribution claims must remain false")
    observations = document.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("ClinVar inventory observations are missing")
    seen: set[str] = set()
    record_count = 0
    for observation in observations:
        if not isinstance(observation, Mapping) or observation.get("depth") not in {0, 1, 2}:
            raise ValueError("ClinVar observation contract is invalid")
        url = str(observation.get("surface_url", ""))
        parsed = urllib.parse.urlsplit(url)
        if (
            parsed.scheme != "https"
            or parsed.hostname != "ftp.ncbi.nlm.nih.gov"
            or not parsed.path.startswith("/pub/clinvar/")
            or url in seen
        ):
            raise ValueError("ClinVar observation URL is unsafe or duplicated")
        seen.add(url)
        records = observation.get("records")
        if not isinstance(records, list):
            raise ValueError("ClinVar observation records must be a list")
        for record in records:
            if not isinstance(record, Mapping):
                raise ValueError("ClinVar record contract is invalid")
            if record.get("byte_route") != document["byte_route"]:
                raise ValueError("ClinVar record byte route drifted")
            if any(key in record for key in ("content", "body", "abstract", "full_text")):
                raise ValueError("ClinVar metadata inventory retained content")
            record_url = urllib.parse.urlsplit(str(record.get("source_url", "")))
            if (
                record_url.scheme != "https"
                or record_url.hostname != "ftp.ncbi.nlm.nih.gov"
                or not record_url.path.startswith("/pub/clinvar/")
            ):
                raise ValueError("ClinVar record URL is unsafe")
        record_count += len(records)
    canonical = {key: value for key, value in document.items() if key != "inventory_sha256"}
    digest = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if document.get("inventory_sha256") != digest:
        raise ValueError("ClinVar inventory fingerprint mismatch")
    exhausted = document.get("exhausted_within_scope") is True
    if exhausted != (document.get("frontier_queue_count") == 0):
        raise ValueError("ClinVar frontier queue and exhaustion state differ")
    return {
        "observations": len(observations),
        "records": record_count,
        "exhausted_within_scope": exhausted,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--max-requests", type=int, default=80)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--delay-seconds", type=float, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.delay_seconds < 1:
        raise ValueError("live discovery delay must be at least one second")
    payload = discover(
        observed_at=args.observed_at,
        max_requests=args.max_requests,
        max_depth=args.max_depth,
        delay_seconds=args.delay_seconds,
    )
    validate_inventory(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
