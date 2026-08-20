#!/usr/bin/env python3
"""Run the authorized Track 007 v0.2.1 Option A metadata-only pilot."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

LANGUAGES = {
    "en": "rare disease burden",
    "es": "carga de enfermedades raras",
    "pt": "carga de doenças raras",
    "fr": "fardeau des maladies rares",
}
REGIONS = {
    "americas": ["AR", "BR", "CA", "CL", "CO", "MX", "US"],
    "europe": ["DE", "ES", "FR", "GB", "IT", "NL", "PL", "SE"],
    "western_pacific": ["AU", "CN", "JP", "KR", "NZ", "PH"],
}
PROVIDERS = ("crossref", "github", "zenodo", "huggingface_datasets")
USER_AGENT = "RareBurden-Commons-Track-007/0.2.1 (bounded metadata pilot)"


def _retrieved_at() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _request(provider: str, query: str) -> tuple[str, bytes, int, str]:
    if provider == "crossref":
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
            {"query": query, "rows": 10, "select": "DOI,title,type,publisher,URL"}
        )
    elif provider == "github":
        url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
            {"q": query, "per_page": 10, "page": 1}
        )
    elif provider == "zenodo":
        url = "https://zenodo.org/api/records/?" + urllib.parse.urlencode(
            {"q": query, "size": 10, "page": 1}
        )
    else:
        url = "https://huggingface.co/api/datasets?" + urllib.parse.urlencode(
            {"search": query, "limit": 10, "skip": 0}
        )
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return url, response.read(), response.status, response.geturl()


def _identifiers(provider: str, payload: Any) -> list[str]:
    if provider == "crossref":
        items = payload.get("message", {}).get("items", [])
        return [str(item["DOI"]).casefold() for item in items if item.get("DOI")]
    if provider == "github":
        return [
            str(item["full_name"] if item.get("full_name") else item["id"])
            for item in payload.get("items", [])
            if item.get("full_name") or item.get("id")
        ]
    if provider == "zenodo":
        return [
            str(item["id"] if item.get("id") else item["doi"])
            for item in payload.get("hits", {}).get("hits", [])
            if item.get("id") or item.get("doi")
        ]
    return [str(item["id"]) for item in payload if item.get("id")]


def _provider_total(provider: str, payload: Any) -> int | str:
    if provider == "crossref":
        return payload.get("message", {}).get("total-results", "not_reported")
    if provider == "github":
        return payload.get("total_count", "not_reported")
    if provider == "zenodo":
        return payload.get("hits", {}).get("total", "not_reported")
    return "not_reported"


def capture(*, output: Path, delay_seconds: float = 1.0) -> dict[str, Any]:
    if delay_seconds < 1:
        raise ValueError("delay_seconds must be at least one second")
    started = _retrieved_at()
    observations: list[dict[str, Any]] = []
    stopped = False
    stop_reason = "pilot_cells_exhausted"
    for language, language_query in LANGUAGES.items():
        for region, country_scope in REGIONS.items():
            query = f"{language_query} {region.replace('_', ' ')}"
            for provider in PROVIDERS:
                if observations:
                    time.sleep(delay_seconds)
                try:
                    request_url, body, status, final_url = _request(provider, query)
                    digest = "sha256:" + hashlib.sha256(body).hexdigest()
                    payload = json.loads(body)
                    identifiers = _identifiers(provider, payload)
                    observations.append(
                        {
                            "protocol_version": "0.2.1",
                            "language_stratum": language,
                            "region_stratum": region,
                            "country_scope": country_scope,
                            "provider": provider,
                            "query_utf8": query,
                            "request_url": request_url,
                            "final_url": final_url,
                            "retrieved_at_utc": _retrieved_at(),
                            "http_status": status,
                            "response_sha256": digest,
                            "observed_identifiers": identifiers,
                            "provider_total_or_cap": _provider_total(provider, payload),
                            "stop_reason": "page_budget_reached",
                            "missingness": "observed" if identifiers else "unknown",
                        }
                    )
                except Exception as exc:
                    observations.append(
                        {
                            "protocol_version": "0.2.1",
                            "language_stratum": language,
                            "region_stratum": region,
                            "country_scope": country_scope,
                            "provider": provider,
                            "query_utf8": query,
                            "status": "stopped",
                            "error_type": type(exc).__name__,
                            "missingness": "not_assessable",
                        }
                    )
                    stopped = True
                    stop_reason = "provider_or_transport_failure"
                    break
            if stopped:
                break
        if stopped:
            break
    result = {
        "schema_version": "RBC-LAND-007-V021-PILOT-v0.1.0",
        "status": "stopped_fail_closed" if stopped else "bounded_observation_complete",
        "started_at_utc": started,
        "selected_option": "A",
        "planned_cells": 48,
        "observations": observations,
        "cells_observed": len(observations),
        "stop_reason": stop_reason,
        "raw_response_retention": "none",
        "claims": ["bounded_public_endpoint_observation_only"],
        "prohibited_claims": [
            "global_coverage",
            "representativeness",
            "community_approval",
            "novelty",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    capture(output=args.output)
