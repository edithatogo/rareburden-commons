#!/usr/bin/env python3
"""Emit a bounded Track 007 public-metadata discovery log as JSON.

The output is deliberately discovery-only. It is suitable for review and later
screening, but it does not establish completeness, novelty, or external review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import urllib.parse
import urllib.request
from typing import Any

QUERIES = (
    "rare disease burden",
    "rare disease registry",
    "rare disease ontology",
    "rare disease prevalence",
    "rare disease cost",
)
USER_AGENT = "RareBurden-Commons-Track-007/0.3 (public metadata discovery)"


def _routes(query: str) -> tuple[tuple[str, str], ...]:
    return (
        (
            "github",
            "https://api.github.com/search/repositories?"
            + urllib.parse.urlencode({"q": query, "per_page": 10}),
        ),
        (
            "zenodo",
            "https://zenodo.org/api/records/?" + urllib.parse.urlencode({"q": query, "size": 10}),
        ),
        (
            "huggingface_datasets",
            "https://huggingface.co/api/datasets?"
            + urllib.parse.urlencode({"search": query, "limit": 10}),
        ),
        (
            "crossref",
            "https://api.crossref.org/works?"
            + urllib.parse.urlencode(
                {
                    "query.bibliographic": query,
                    "rows": 10,
                    "select": "DOI,title,publisher,published",
                }
            ),
        ),
    )


def _summary(registry: str, payload: Any) -> tuple[int | str, list[str]]:
    if registry == "github":
        return int(payload["total_count"]), [item["full_name"] for item in payload["items"]]
    if registry == "zenodo":
        hits = payload["hits"]
        return int(hits["total"]), [str(item["id"]) for item in hits["hits"]]
    if registry == "huggingface_datasets":
        return "not_reported", [item["id"] for item in payload]
    message = payload["message"]
    return int(message["total-results"]), [item["DOI"] for item in message["items"]]


def retrieve(registry: str, query: str, endpoint: str, timeout: int) -> dict[str, Any]:
    retrieved_at = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    request = urllib.request.Request(
        endpoint,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        status = response.status
    total, identifiers = _summary(registry, json.loads(body))
    return {
        "registry": registry,
        "query_string": query,
        "endpoint": endpoint,
        "retrieved_at_utc": retrieved_at,
        "http_status": status,
        "result_total": total,
        "first_page_items": len(identifiers),
        "first_page_ids": identifiers,
        "response_sha256": "sha256:" + hashlib.sha256(body).hexdigest(),
        "raw_export": "not_retained",
        "screening_status": "unscreened",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    records = [
        retrieve(registry, query, endpoint, args.timeout)
        for query in QUERIES
        for registry, endpoint in _routes(query)
    ]
    print(
        json.dumps(
            {
                "protocol_version": "RBC-LAND-007-v0.2.0",
                "status": "discovery_only",
                "records": records,
                "limitations": [
                    "Counts are retrieval-time observations, not fixed catalogue facts.",
                    "Provider ranking and broad full-text matching require eligibility screening.",
                    "No completeness, novelty, partnership, registration, or external-review "
                    "claim is implied.",
                    "OSF is excluded from this active refresh under the recorded owner deferral.",
                ],
            },
            indent=2,
            sort_keys=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
