#!/usr/bin/env python3
"""Resolve restricted DOI records from public Crossref metadata only.

The publisher locator is never fetched.  Response bodies are hashed and
discarded; only citation-level fields and closed-vocabulary signals survive.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

USER_AGENT = "RareBurden-Commons-Track-007/0.3 (lawful public metadata alternative)"
SCOPE_TERMS = ("rare disease", "rare-disease", "orphan", "cystinosis", "insulinoma")
CONTRIBUTION_TERMS = (
    "burden",
    "care",
    "classification",
    "cost",
    "demographic",
    "economic",
    "inheritance",
    "measurement",
    "ontology",
    "outcome",
    "registry",
)


def _normalize(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.casefold()).split())


def fetch(url: str, timeout: int) -> tuple[bytes, int, str]:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(), response.status, response.geturl()
    except urllib.error.HTTPError as exc:
        return exc.read(), exc.code, exc.geturl()


def resolve(
    eligibility_raw: bytes,
    *,
    fetch_record: Callable[[str, int], tuple[bytes, int, str]] = fetch,
    timeout: int = 30,
    delay_seconds: float = 0.0,
    observed_at_utc: str | None = None,
) -> dict[str, Any]:
    eligibility = json.loads(eligibility_raw)
    pending = [
        item
        for item in eligibility["decisions"]
        if item["eligibility_state"] == "pending_lawful_access"
    ]
    observed_at_utc = observed_at_utc or (
        dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    resolutions: list[dict[str, Any]] = []
    for index, item in enumerate(pending):
        identifier = item["identifier"]
        if not isinstance(identifier, str) or not identifier.startswith("10."):
            raise ValueError("restricted alternative requires a DOI identifier")
        if index and delay_seconds:
            time.sleep(delay_seconds)
        url = "https://api.crossref.org/works/" + urllib.parse.quote(identifier, safe="")
        body, status, final_url = fetch_record(url, timeout)
        response_sha256 = "sha256:" + hashlib.sha256(body).hexdigest()
        if status != 200:
            resolutions.append(
                {
                    "canonical_key": item["canonical_key"],
                    "identifier": identifier,
                    "request_url": url,
                    "final_url": final_url,
                    "http_status": status,
                    "response_sha256": response_sha256,
                    "evidence_sha256": response_sha256,
                    "observed_at_utc": observed_at_utc,
                    "decision": "pending_lawful_access",
                    "reason": "public_metadata_alternative_unavailable",
                }
            )
            continue
        payload = json.loads(body)
        message = payload.get("message")
        if not isinstance(message, dict):
            raise ValueError("Crossref response lacks message object")
        titles = message.get("title") or []
        title = titles[0] if isinstance(titles, list) and titles else ""
        if not isinstance(title, str):
            raise ValueError("Crossref title is not text")
        work_type = message.get("type")
        publisher = message.get("publisher")
        canonical_url = message.get("URL") or item["canonical_url"]
        if not all(value is None or isinstance(value, str) for value in (work_type, publisher)):
            raise ValueError("Crossref citation fields have invalid types")
        normalized = _normalize(title)
        scope = any(_normalize(term) in normalized for term in SCOPE_TERMS)
        contribution = any(_normalize(term) in normalized for term in CONTRIBUTION_TERMS)
        decision = "include" if scope and contribution else "uncertain"
        resolutions.append(
            {
                "canonical_key": item["canonical_key"],
                "identifier": identifier,
                "request_url": url,
                "final_url": final_url,
                "http_status": status,
                "response_sha256": response_sha256,
                "evidence_sha256": response_sha256,
                "observed_at_utc": observed_at_utc,
                "title": " ".join(title.split()),
                "canonical_url": canonical_url,
                "work_type": work_type,
                "publisher": publisher,
                "scope_signal": scope,
                "contribution_signal": contribution,
                "decision": decision,
                "reason": "public_crossref_title_supports_bounded_adjacency"
                if decision == "include"
                else "public_crossref_metadata_insufficient_for_content_decision",
            }
        )
    counts = {
        state: sum(item["decision"] == state for item in resolutions)
        for state in ("include", "uncertain", "pending_lawful_access")
    }
    return {
        "workflow_version": "RBC-LAND-007-LAWFUL-ALTERNATIVES-v0.1.0",
        "source_sha256": "sha256:" + hashlib.sha256(eligibility_raw).hexdigest(),
        "counts": counts,
        "content_retention": "citation_metadata_and_hashes_only_no_publisher_content",
        "resolutions": resolutions,
        "limitations": [
            "Crossref metadata is an alternative citation observation, not publisher access.",
            "Uncertain or unavailable records remain pending and are never excluded.",
            "No abstract, body, description or full text is retained.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("eligibility", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    args = parser.parse_args()
    result = resolve(
        args.eligibility.read_bytes(), timeout=args.timeout, delay_seconds=args.delay_seconds
    )
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
