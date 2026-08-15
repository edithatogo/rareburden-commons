#!/usr/bin/env python3
"""Capture bounded, hash-addressed pages for Track 007 public searches.

This workflow deliberately reports capture mechanics rather than search
completeness. A provider-declared total or an exhausted page sequence describes
only the public endpoint and query at the recorded retrieval time.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

QUERIES = (
    "rare disease burden",
    "rare disease registry",
    "rare disease ontology",
    "rare disease prevalence",
    "rare disease cost",
)
USER_AGENT = "RareBurden-Commons-Track-007/0.3 (bounded pagination capture)"


class CaptureError(RuntimeError):
    """Raised when a page chain cannot be captured without ambiguity."""


@dataclass(frozen=True)
class PageRequest:
    registry: str
    query: str
    page_number: int
    url: str


def build_request(registry: str, query: str, page: int, page_size: int) -> PageRequest:
    if page < 1 or page_size < 1:
        raise CaptureError("page and page_size must be positive")
    if registry == "github":
        params = {"q": query, "page": page, "per_page": page_size}
        base = "https://api.github.com/search/repositories"
    elif registry == "zenodo":
        params = {"q": query, "page": page, "size": page_size}
        base = "https://zenodo.org/api/records/"
    elif registry == "huggingface_datasets":
        params = {"search": query, "limit": page_size, "skip": (page - 1) * page_size}
        base = "https://huggingface.co/api/datasets"
    else:
        raise CaptureError(f"unsupported registry: {registry}")
    return PageRequest(registry, query, page, base + "?" + urllib.parse.urlencode(params))


def _records_and_total(registry: str, payload: Any) -> tuple[list[dict[str, Any]], int | None]:
    if registry == "github":
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise CaptureError("github response lacks items")
        records = payload["items"]
        total = payload.get("total_count")
    elif registry == "zenodo":
        hits = payload.get("hits") if isinstance(payload, dict) else None
        if not isinstance(hits, dict) or not isinstance(hits.get("hits"), list):
            raise CaptureError("zenodo response lacks hits.hits")
        records = hits["hits"]
        total = hits.get("total")
    else:
        if not isinstance(payload, list):
            raise CaptureError("huggingface response is not a list")
        records = payload
        total = None
    if total is not None and (not isinstance(total, int) or total < 0):
        raise CaptureError(f"{registry} response has invalid total")
    return records, total


def _identifier(registry: str, record: dict[str, Any]) -> str:
    candidates = {
        "github": ("full_name", "id"),
        "zenodo": ("id", "doi"),
        "huggingface_datasets": ("id",),
    }[registry]
    for field in candidates:
        value = record.get(field)
        if value not in (None, ""):
            return str(value)
    raise CaptureError(f"{registry} record lacks a stable identifier")


def fetch(request: PageRequest, timeout: int) -> tuple[bytes, int, str]:
    req = urllib.request.Request(
        request.url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read(), response.status, response.geturl()


def capture_query(
    registry: str,
    query: str,
    *,
    page_size: int,
    max_pages: int,
    timeout: int,
    fetch_page: Callable[[PageRequest, int], tuple[bytes, int, str]] = fetch,
    retrieved_at_utc: str | None = None,
) -> dict[str, Any]:
    if max_pages < 1:
        raise CaptureError("max_pages must be positive")
    retrieved_at_utc = retrieved_at_utc or (
        dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    pages: list[dict[str, Any]] = []
    seen: set[str] = set()
    declared_total: int | None = None
    stop_reason = "page_budget_reached"

    for page_number in range(1, max_pages + 1):
        request = build_request(registry, query, page_number, page_size)
        body, status, final_url = fetch_page(request, timeout)
        if status != 200:
            raise CaptureError(f"{registry} page {page_number} returned HTTP {status}")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise CaptureError(f"{registry} page {page_number} returned invalid JSON") from exc
        records, page_total = _records_and_total(registry, payload)
        if declared_total is None:
            declared_total = page_total
        elif page_total is not None and page_total != declared_total:
            raise CaptureError(f"{registry} declared total changed during capture")
        identifiers = [_identifier(registry, record) for record in records]
        duplicates = sorted(identifier for identifier in identifiers if identifier in seen)
        if duplicates:
            raise CaptureError(
                f"{registry} page {page_number} repeated identifiers from prior pages: {duplicates}"
            )
        seen.update(identifiers)
        pages.append(
            {
                "page_number": page_number,
                "request_url": request.url,
                "final_url": final_url,
                "http_status": status,
                "response_sha256": "sha256:" + hashlib.sha256(body).hexdigest(),
                "item_count": len(records),
                "identifiers": identifiers,
            }
        )
        if not records:
            stop_reason = "empty_page_observed"
            break
        if declared_total is not None and len(seen) >= declared_total:
            stop_reason = "provider_total_reached"
            break
        if len(records) < page_size:
            stop_reason = "short_page_observed"
            break

    # GitHub Search exposes at most 1,000 results even when total_count is larger.
    provider_cap = 1000 if registry == "github" else None
    if provider_cap is not None and declared_total is not None and declared_total > provider_cap:
        capture_ceiling = provider_cap
        provider_limited = True
    else:
        capture_ceiling = declared_total
        provider_limited = False

    return {
        "registry": registry,
        "query_string": query,
        "retrieved_at_utc": retrieved_at_utc,
        "page_size": page_size,
        "max_pages": max_pages,
        "pages_captured": len(pages),
        "occurrences_captured": sum(page["item_count"] for page in pages),
        "unique_identifiers_captured": len(seen),
        "provider_declared_total": declared_total if declared_total is not None else "not_reported",
        "provider_capture_ceiling": (
            capture_ceiling if capture_ceiling is not None else "not_reported"
        ),
        "provider_limited": provider_limited,
        "stop_reason": stop_reason,
        "capture_complete_for_declared_total": bool(
            declared_total is not None
            and not provider_limited
            and len(seen) == declared_total
            and stop_reason == "provider_total_reached"
        ),
        "pages": pages,
        "claim_boundary": (
            "Evidence covers only the recorded public endpoint pages at this retrieval time; "
            "it does not establish landscape, scholarly, repository, language, "
            "or temporal completeness."
        ),
    }


def _fixture_fetcher(fixture_dir: Path) -> Callable[[PageRequest, int], tuple[bytes, int, str]]:
    def fixture_fetch(request: PageRequest, _timeout: int) -> tuple[bytes, int, str]:
        slug = hashlib.sha256(request.query.encode("utf-8")).hexdigest()[:12]
        path = fixture_dir / f"{request.registry}-{slug}-page-{request.page_number}.json"
        if not path.is_file():
            raise CaptureError(f"missing fixture page: {path.name}")
        return path.read_bytes(), 200, request.url

    return fixture_fetch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        choices=("github", "zenodo", "huggingface_datasets"),
        required=True,
    )
    parser.add_argument("--query", action="append", dest="queries")
    parser.add_argument("--page-size", type=int, default=25)
    parser.add_argument("--max-pages", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--retrieved-at-utc")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    fetch_page = _fixture_fetcher(args.fixture_dir) if args.fixture_dir else fetch
    captures = [
        capture_query(
            args.registry,
            query,
            page_size=args.page_size,
            max_pages=args.max_pages,
            timeout=args.timeout,
            fetch_page=fetch_page,
            retrieved_at_utc=args.retrieved_at_utc,
        )
        for query in (args.queries or QUERIES)
    ]
    rendered = (
        json.dumps(
            {
                "schema_version": "RBC-LAND-007-PAGES-v0.1.0",
                "status": "bounded_capture_only",
                "captures": captures,
                "limitations": [
                    "Captured pages are not a claim of ecosystem completeness or "
                    "representativeness.",
                    "Provider totals, rankings and public metadata can change after retrieval.",
                    "Page budgets and provider caps are reported as incomplete rather "
                    "than inferred complete.",
                    "External registration, methods challenge and patient/community "
                    "interpretation remain pending.",
                ],
            },
            indent=2,
        )
        + "\n"
    )
    if args.output:
        try:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(rendered)
        except FileExistsError as exc:
            raise CaptureError(f"refusing to overwrite capture: {args.output}") from exc
        except OSError as exc:
            raise CaptureError(f"cannot write capture: {args.output}: {exc}") from exc
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
