#!/usr/bin/env python3
"""Observe minimal current metadata for Track 007 live-only identifiers.

Descriptions are inspected transiently for closed-vocabulary signals but are
not retained.  An absent signal or failed request remains uncertain and is
never converted to exclusion evidence.
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

USER_AGENT = "RareBurden-Commons-Track-007/0.3 (bounded identifier metadata observation)"
SCOPE_TERMS = ("rare disease", "rare-disease", "orphanet", "ordo")
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


def _request_url(registry: str, identifier: str) -> str:
    if registry == "github":
        parts = identifier.split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError(f"invalid GitHub repository identifier: {identifier}")
        return "https://api.github.com/repos/" + "/".join(
            urllib.parse.quote(part, safe="") for part in parts
        )
    if registry == "zenodo" and identifier.isdigit():
        return f"https://zenodo.org/api/records/{identifier}"
    raise ValueError(f"unsupported live metadata identifier: {registry}:{identifier}")


def fetch(url: str, timeout: int) -> tuple[bytes, int, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(), response.status, response.geturl()
    except urllib.error.HTTPError as exc:
        return exc.read(), exc.code, exc.geturl()


def _minimal_metadata(registry: str, identifier: str, payload: Any) -> tuple[str, str, str]:
    if not isinstance(payload, dict):
        raise ValueError("metadata response is not an object")
    if registry == "github":
        title = payload.get("name") or payload.get("full_name") or ""
        canonical_url = payload.get("html_url") or ""
        description = payload.get("description") or ""
    else:
        metadata = payload.get("metadata")
        links = payload.get("links")
        if not isinstance(metadata, dict) or not isinstance(links, dict):
            raise ValueError("Zenodo response lacks metadata or links")
        title = metadata.get("title") or ""
        canonical_url = links.get("html") or f"https://zenodo.org/records/{identifier}"
        description = metadata.get("description") or ""
    if not all(isinstance(value, str) for value in (title, canonical_url, description)):
        raise ValueError("metadata fields must be text")
    return " ".join(title.split()), canonical_url, description


def observe(
    reconciliation_raw: bytes,
    *,
    fetch_record: Callable[[str, int], tuple[bytes, int, str]] = fetch,
    timeout: int = 30,
    delay_seconds: float = 0.0,
    observed_at_utc: str | None = None,
) -> dict[str, Any]:
    reconciliation = json.loads(reconciliation_raw)
    pending = [
        record
        for record in reconciliation["records"]
        if record["reconciliation_state"] == "pending_metadata_retrieval"
    ]
    observed_at_utc = observed_at_utc or (
        dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    observations: list[dict[str, Any]] = []
    for index, record in enumerate(pending):
        registry, _, _ = record["identifier_key"].partition(":")
        identifier = record["identifier"]
        url = _request_url(registry, identifier)
        if index and delay_seconds:
            time.sleep(delay_seconds)
        try:
            body, status, final_url = fetch_record(url, timeout)
            response_hash = "sha256:" + hashlib.sha256(body).hexdigest()
            if status != 200:
                observations.append(
                    {
                        "identifier_key": record["identifier_key"],
                        "identifier": identifier,
                        "registry": registry,
                        "request_url": url,
                        "final_url": final_url,
                        "http_status": status,
                        "response_sha256": response_hash,
                        "observed_at_utc": observed_at_utc,
                        "title": None,
                        "canonical_url": None,
                        "description_retained": False,
                        "scope_signal": "not_assessable",
                        "contribution_signal": "not_assessable",
                        "screening_decision": "pending_observation_retry",
                    }
                )
                continue
            payload = json.loads(body)
            title, canonical_url, description = _minimal_metadata(registry, identifier, payload)
            normalized = _normalize(" ".join((title, description, identifier)))
            scope = any(_normalize(term) in normalized for term in SCOPE_TERMS)
            contribution = any(_normalize(term) in normalized for term in CONTRIBUTION_TERMS)
            decision = (
                "include_for_content_assessment"
                if scope and contribution
                else "uncertain_public_metadata_signal"
            )
            observations.append(
                {
                    "identifier_key": record["identifier_key"],
                    "identifier": identifier,
                    "registry": registry,
                    "request_url": url,
                    "final_url": final_url,
                    "http_status": status,
                    "response_sha256": response_hash,
                    "observed_at_utc": observed_at_utc,
                    "title": title,
                    "canonical_url": canonical_url,
                    "description_retained": False,
                    "scope_signal": scope,
                    "contribution_signal": contribution,
                    "screening_decision": decision,
                }
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            observations.append(
                {
                    "identifier_key": record["identifier_key"],
                    "identifier": identifier,
                    "registry": registry,
                    "request_url": url,
                    "final_url": None,
                    "http_status": None,
                    "response_sha256": None,
                    "observed_at_utc": observed_at_utc,
                    "title": None,
                    "canonical_url": None,
                    "description_retained": False,
                    "scope_signal": "not_assessable",
                    "contribution_signal": "not_assessable",
                    "screening_decision": "pending_observation_retry",
                    "error_class": type(exc).__name__,
                }
            )

    counts: dict[str, int] = {}
    for item in observations:
        state = item["screening_decision"]
        counts[state] = counts.get(state, 0) + 1
    return {
        "workflow_version": "RBC-LAND-007-LIVE-METADATA-v0.1.0",
        "status": "bounded_current_metadata_observation",
        "reconciliation_sha256": "sha256:" + hashlib.sha256(reconciliation_raw).hexdigest(),
        "observation_count": len(observations),
        "counts": dict(sorted(counts.items())),
        "content_retention": "minimal_metadata_only_description_inspected_transiently_not_retained",
        "observations": observations,
        "limitations": [
            "These current identifier observations do not reconstruct capture-time "
            "ranking or bytes.",
            "A missing or ambiguous signal remains pending and is never an exclusion.",
            "No abstract, description, body or full-text bytes are retained.",
            "Inclusion is for content assessment, not final eligibility, quality, "
            "coverage or novelty.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reconciliation", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    args = parser.parse_args()
    result = observe(
        args.reconciliation.read_bytes(),
        timeout=args.timeout,
        delay_seconds=args.delay_seconds,
    )
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
