#!/usr/bin/env python3
"""Capture a strictly bounded Crossref and multilingual/community expansion."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

USER_AGENT = "RareBurden-Commons-Track-007/0.3 (bounded bibliographic expansion)"
QUERIES = (
    ("rare disease burden", "en", "frozen"),
    ("rare disease registry", "en", "frozen"),
    ("rare disease ontology", "en", "frozen"),
    ("rare disease prevalence", "en", "frozen"),
    ("rare disease cost", "en", "frozen"),
    ("enfermedades raras carga", "es", "multilingual"),
    ("maladies rares fardeau", "fr", "multilingual"),
    ("doenças raras carga", "pt", "multilingual"),
    ("seltene krankheiten krankheitslast", "de", "multilingual"),
    ("rare disease patient organization", "en", "community"),
    ("rare disease community led", "en", "community"),
    ("organización pacientes enfermedades raras", "es", "community_multilingual"),
)


def fetch(url: str, timeout: int) -> tuple[bytes, int, str]:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(), response.status, response.geturl()


def capture(
    *,
    fetch_page: Callable[[str, int], tuple[bytes, int, str]] = fetch,
    rows: int = 20,
    max_pages: int = 2,
    delay_seconds: float = 0.0,
    timeout: int = 30,
    retrieved_at_utc: str | None = None,
) -> dict[str, Any]:
    if not 1 <= rows <= 100 or not 1 <= max_pages <= 3:
        raise ValueError("rows must be 1..100 and max_pages 1..3")
    retrieved_at_utc = retrieved_at_utc or dt.datetime.now(dt.UTC).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    captures: list[dict[str, Any]] = []
    request_count = 0
    for query, declared_language, family in QUERIES:
        cursor = "*"
        pages: list[dict[str, Any]] = []
        seen: set[str] = set()
        provider_total: int | None = None
        for page_number in range(1, max_pages + 1):
            params = {
                "query": query,
                "rows": rows,
                "cursor": cursor,
                "select": "DOI,title,URL,type,publisher",
            }
            url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
            if request_count and delay_seconds:
                time.sleep(delay_seconds)
            request_count += 1
            body, status, final_url = fetch_page(url, timeout)
            if status != 200:
                raise ValueError(f"Crossref query returned HTTP {status}")
            payload = json.loads(body)
            message = payload.get("message") if isinstance(payload, dict) else None
            if not isinstance(message, dict) or not isinstance(message.get("items"), list):
                raise ValueError("Crossref response lacks message.items")
            total = message.get("total-results")
            if not isinstance(total, int) or total < 0:
                raise ValueError("Crossref response lacks a valid total")
            if provider_total is None:
                provider_total = total
            elif total != provider_total:
                raise ValueError("Crossref total changed within capture")
            records: list[dict[str, Any]] = []
            for item in message["items"]:
                doi = str(item.get("DOI") or "").casefold()
                if not doi or doi in seen:
                    raise ValueError("Crossref page contains missing or repeated DOI")
                seen.add(doi)
                titles = item.get("title") or []
                title = str(titles[0]) if isinstance(titles, list) and titles else ""
                records.append(
                    {
                        "doi": doi,
                        "title": title,
                        "canonical_url": str(item.get("URL") or f"https://doi.org/{doi}"),
                        "work_type": str(item.get("type") or ""),
                        "record_language": str(item.get("language") or "not_reported"),
                        "publisher": str(item.get("publisher") or ""),
                    }
                )
            next_cursor = message.get("next-cursor")
            pages.append(
                {
                    "page_number": page_number,
                    "request_url": url,
                    "final_url": final_url,
                    "http_status": status,
                    "response_sha256": "sha256:" + hashlib.sha256(body).hexdigest(),
                    "records": records,
                }
            )
            if len(records) < rows or not isinstance(next_cursor, str) or not next_cursor:
                break
            cursor = next_cursor
        language_counts: dict[str, int] = {}
        for page in pages:
            for record in page["records"]:
                language = record["record_language"]
                language_counts[language] = language_counts.get(language, 0) + 1
        captures.append(
            {
                "query_string": query,
                "query_family": family,
                "declared_query_language": declared_language,
                "geography_sampling": "not_measured",
                "provider_total": provider_total,
                "pages_captured": len(pages),
                "unique_dois_captured": len(seen),
                "record_language_counts": dict(sorted(language_counts.items())),
                "pages": pages,
            }
        )
    return {
        "workflow_version": "RBC-LAND-007-CROSSREF-EXPANSION-v0.1.0",
        "status": "bounded_ranked_bibliographic_observation",
        "retrieved_at_utc": retrieved_at_utc,
        "rows": rows,
        "max_pages": max_pages,
        "request_budget": len(QUERIES) * max_pages,
        "requests_made": request_count,
        "captures": captures,
        "limitations": [
            "Crossref is one bibliographic index and ranked results are not systematic coverage.",
            "Declared query language is not inferred record language or geography.",
            "Missing Crossref language metadata remains missing and is not imputed.",
            "Community query terms do not establish community authorship, leadership, "
            "legitimacy, or approval.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rows", type=int, default=20)
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    args = parser.parse_args()
    result = capture(rows=args.rows, max_pages=args.max_pages, delay_seconds=args.delay_seconds)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
