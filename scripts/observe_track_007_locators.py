#!/usr/bin/env python3
"""Observe Track 007 public locators without retaining response bodies."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def observe(item: dict[str, Any], checked_at: str, timeout: float) -> dict[str, Any]:
    url = item["canonical_url"]
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "RareBurdenCommons/Track007-locator-audit"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return {
                "canonical_key": item["canonical_key"],
                "requested_url": url,
                "method": "HEAD",
                "checked_at": checked_at,
                "http_status": response.status,
                "final_url": response.url,
                "content_type": response.headers.get_content_type(),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        return {
            "canonical_key": item["canonical_key"],
            "requested_url": url,
            "method": "HEAD",
            "checked_at": checked_at,
            "http_status": exc.code,
            "final_url": exc.url,
            "content_type": exc.headers.get_content_type() if exc.headers else None,
            "error": None,
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "canonical_key": item["canonical_key"],
            "requested_url": url,
            "method": "HEAD",
            "checked_at": checked_at,
            "http_status": None,
            "final_url": None,
            "content_type": None,
            "error": type(exc).__name__,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("screening", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    screening = json.loads(args.screening.read_text(encoding="utf-8"))
    retained = [item for item in screening["decisions"] if item["decision"] == "include"]
    checked_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        observations = list(
            executor.map(lambda item: observe(item, checked_at, args.timeout), retained)
        )
    observations.sort(key=lambda item: item["canonical_key"])
    document = {
        "observation_version": "RBC-LAND-007-LOCATORS-v0.1.0",
        "checked_at": checked_at,
        "method": "HEAD only; response bodies were not read or retained",
        "observations": observations,
        "limitations": [
            "A HEAD response is a bounded locator observation, not a full-text assessment.",
            "Transient, restricted and unsupported-HEAD responses remain unresolved.",
        ],
    }
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
