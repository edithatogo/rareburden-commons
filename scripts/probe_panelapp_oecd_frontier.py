#!/usr/bin/env python3
"""Make bounded metadata-only PanelApp/OECD frontier observations."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

USER_AGENT = "rareburden-metadata-frontier/1 (+https://github.com/edithatogo/rareburden-commons)"


def fetch(
    url: str, *, timeout: int = 60, max_bytes: int = 2_000_000
) -> tuple[bytes, dict[str, str], int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError("metadata response exceeded byte budget")
        return body, dict(response.headers.items()), response.status, response.geturl()


def bounded_observation(source_id: str, url: str, *, delay_seconds: float = 2.0) -> dict[str, Any]:
    if not url.startswith("https://"):
        raise ValueError("frontier URL must use HTTPS")
    if delay_seconds < 1.0:
        raise ValueError("delay_seconds must be at least one second")
    allowed_hosts = {
        "panelapp-australia": "panelapp-aus.org",
        "oecd-health-statistics-dataflow": "sdmx.oecd.org",
    }
    if source_id not in allowed_hosts:
        raise ValueError("source_id is not approved for metadata probing")
    if urllib.parse.urlsplit(url).hostname != allowed_hosts[source_id]:
        raise ValueError("frontier URL host is not approved for source_id")
    time.sleep(delay_seconds)
    body, headers, status, final_url = fetch(url)
    if urllib.parse.urlsplit(final_url).hostname != allowed_hosts[source_id]:
        raise ValueError("frontier request redirected outside approved host")
    result: dict[str, Any] = {
        "source_id": source_id,
        "url": url,
        "final_url": final_url,
        "http_status": status,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "content_type": headers.get("Content-Type", "unknown"),
        "raw_response_retained": False,
        "production_activation": False,
    }
    if source_id == "panelapp-australia":
        payload = json.loads(body)
        result["bounded_metadata"] = {
            "reported_count": payload.get("count"),
            "has_next_page": bool(payload.get("next")),
            "page_result_count": len(payload.get("results", [])),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source_id", choices=("panelapp-australia", "oecd-health-statistics-dataflow")
    )
    parser.add_argument("--url", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    args = parser.parse_args()
    receipt = {
        "schema_version": "1.0",
        "status": "bounded_metadata_hash_observation",
        "observation": bounded_observation(
            args.source_id, args.url, delay_seconds=args.delay_seconds
        ),
        "claims": {
            "raw_archival": False,
            "dataset_terms_clear": False,
            "version_completeness": False,
            "global_representativeness": False,
        },
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
