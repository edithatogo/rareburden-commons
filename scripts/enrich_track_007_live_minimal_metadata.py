#!/usr/bin/env python3
"""Deepen live Track 007 assessment with safe public metadata fields."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

USER_AGENT = "RareBurden-Commons-Track-007/0.3 (bounded safe metadata enrichment)"
SCOPE_TERMS = ("rare disease", "rare-disease", "orphanet", "ordo", "orphan disease")
CONTRIBUTION_TERMS = (
    "analysis",
    "burden",
    "classification",
    "cost",
    "data",
    "database",
    "dataset",
    "economic",
    "estimate",
    "infrastructure",
    "measurement",
    "method",
    "model",
    "ontology",
    "platform",
    "prevalence",
    "registry",
    "software",
    "standard",
    "surveillance",
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


def _safe_fields(registry: str, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("metadata response is not an object")
    if registry == "github":
        license_data = payload.get("license")
        return {
            "topics": payload.get("topics") or [],
            "language": payload.get("language"),
            "license_spdx_id": license_data.get("spdx_id")
            if isinstance(license_data, dict)
            else None,
            "archived": payload.get("archived"),
            "fork": payload.get("fork"),
        }
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("Zenodo response lacks metadata")
    resource_type = metadata.get("resource_type")
    return {
        "keywords": metadata.get("keywords") or [],
        "resource_type": resource_type.get("id")
        if isinstance(resource_type, dict)
        else resource_type,
        "language": metadata.get("language"),
        "access_right": metadata.get("access_right"),
    }


def enrich(
    observations_raw: bytes,
    *,
    fetch_record: Callable[[str, int], tuple[bytes, int, str]] = fetch,
    timeout: int = 30,
    delay_seconds: float = 0.0,
    observed_at_utc: str | None = None,
) -> dict[str, Any]:
    source = json.loads(observations_raw)
    observed_at_utc = observed_at_utc or (
        dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    decisions = []
    for index, item in enumerate(source["observations"]):
        if index and delay_seconds:
            time.sleep(delay_seconds)
        body, status, final_url = fetch_record(item["request_url"], timeout)
        response_sha256 = "sha256:" + hashlib.sha256(body).hexdigest()
        base = {
            "identifier_key": item["identifier_key"],
            "identifier": item["identifier"],
            "registry": item["registry"],
            "request_url": item["request_url"],
            "final_url": final_url,
            "http_status": status,
            "response_sha256": response_sha256,
            "observed_at_utc": observed_at_utc,
            "title": item["title"],
            "canonical_url": item["canonical_url"],
        }
        if status != 200:
            decisions.append({**base, "decision": "uncertain", "reason": "metadata_retry_failed"})
            continue
        fields = _safe_fields(item["registry"], json.loads(body))
        values = [item["title"] or ""]
        values.extend(value for value in fields.get("topics", []) if isinstance(value, str))
        values.extend(value for value in fields.get("keywords", []) if isinstance(value, str))
        if isinstance(fields.get("resource_type"), str):
            values.append(fields["resource_type"])
        normalized = _normalize(" ".join(values))
        scope = any(_normalize(term) in normalized for term in SCOPE_TERMS)
        contribution = any(_normalize(term) in normalized for term in CONTRIBUTION_TERMS)
        prior_supported = item.get("screening_decision") == "include_for_content_assessment"
        supported = prior_supported or (scope and contribution)
        decisions.append(
            {
                **base,
                **fields,
                "scope_signal": scope,
                "contribution_signal": contribution,
                "decision": "include" if supported else "uncertain",
                "reason": (
                    "prior_hash_bound_public_signal_preserved"
                    if prior_supported
                    else "safe_metadata_scope_and_contribution_signals"
                )
                if supported
                else "safe_metadata_insufficient_for_content_decision",
            }
        )
    counts = {
        state: sum(item["decision"] == state for item in decisions)
        for state in ("include", "uncertain")
    }
    return {
        "workflow_version": "RBC-LAND-007-LIVE-SAFE-METADATA-v0.1.0",
        "source_sha256": "sha256:" + hashlib.sha256(observations_raw).hexdigest(),
        "counts": counts,
        "content_retention": "titles_topics_keywords_types_access_and_repository_facts_only",
        "decisions": decisions,
        "limitations": [
            "Safe metadata eligibility is adjacency evidence, not content quality or novelty.",
            "Uncertain records are not excluded.",
            "No description, abstract, body or full text is retained.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("observations", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    args = parser.parse_args()
    result = enrich(
        args.observations.read_bytes(), timeout=args.timeout, delay_seconds=args.delay_seconds
    )
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
