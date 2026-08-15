#!/usr/bin/env python3
"""Observe lawful public metadata for pending Track 007 eligibility records.

Response bodies are inspected transiently and represented only by SHA-256,
minimal bibliographic fields, and closed-vocabulary signals. Abstracts,
descriptions, bodies, and full text are never retained.
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

USER_AGENT = "RareBurden-Commons-Track-007/0.3 (bounded public content metadata)"
SCOPE = ("rare disease", "rare-disease", "orphanet", "ordo")
CONTRIBUTION = (
    "burden",
    "cost",
    "data",
    "diagnos",
    "economic",
    "estimate",
    "method",
    "ontology",
    "prevalence",
    "registry",
    "standard",
)
NON_SUBSTANTIVE = ("erratum", "author s response", "correspondence")


def _normalize(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.casefold()).split())


def _request(record: dict[str, Any]) -> tuple[str, str]:
    key = record["canonical_key"]
    if key.startswith("doi:"):
        doi = key.removeprefix("doi:")
        return "crossref", "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    if key.startswith("github:"):
        identifier = record["identifier"]
        return "github", "https://api.github.com/repos/" + "/".join(
            urllib.parse.quote(part, safe="") for part in identifier.split("/")
        )
    raise ValueError(f"unsupported pending record: {key}")


def fetch(url: str, timeout: int) -> tuple[bytes, int, str]:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(), response.status, response.geturl()
    except urllib.error.HTTPError as exc:
        return exc.read(), exc.code, exc.geturl()


def _fields(provider: str, payload: Any) -> tuple[str, str, str, str]:
    if not isinstance(payload, dict):
        raise ValueError("response is not an object")
    if provider == "crossref":
        message = payload.get("message")
        if not isinstance(message, dict):
            raise ValueError("Crossref response lacks message")
        titles = message.get("title") or []
        title = titles[0] if isinstance(titles, list) and titles else ""
        hidden = str(message.get("abstract") or "")
        return str(title), str(message.get("URL") or ""), str(message.get("type") or ""), hidden
    title = str(payload.get("name") or payload.get("full_name") or "")
    return (
        title,
        str(payload.get("html_url") or ""),
        "software",
        str(payload.get("description") or ""),
    )


def resolve(
    eligibility_raw: bytes,
    *,
    fetch_record: Callable[[str, int], tuple[bytes, int, str]] = fetch,
    observed_at_utc: str | None = None,
    delay_seconds: float = 0.0,
    timeout: int = 30,
) -> dict[str, Any]:
    eligibility = json.loads(eligibility_raw)
    pending = [
        d
        for d in eligibility["decisions"]
        if d["eligibility_state"] == "pending_content_assessment"
    ]
    observed_at_utc = observed_at_utc or dt.datetime.now(dt.UTC).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    observations: list[dict[str, Any]] = []
    resolutions: list[dict[str, Any]] = []
    for index, record in enumerate(pending):
        provider, url = _request(record)
        if index and delay_seconds:
            time.sleep(delay_seconds)
        body, status, final_url = fetch_record(url, timeout)
        evidence_hash = "sha256:" + hashlib.sha256(body).hexdigest()
        base = {
            "canonical_key": record["canonical_key"],
            "provider": provider,
            "request_url": url,
            "final_url": final_url,
            "http_status": status,
            "response_sha256": evidence_hash,
            "observed_at_utc": observed_at_utc,
            "abstract_or_description_retained": False,
        }
        if status != 200:
            observations.append({**base, "decision": "pending_public_evidence"})
            continue
        try:
            payload = json.loads(body)
            title, canonical_url, work_type, hidden = _fields(provider, payload)
        except (json.JSONDecodeError, ValueError):
            observations.append({**base, "decision": "pending_public_evidence"})
            continue
        text = _normalize(" ".join((title, hidden, record["identifier"])))
        scope = any(_normalize(term) in text for term in SCOPE)
        contribution = any(_normalize(term) in text for term in CONTRIBUTION)
        non_substantive = any(_normalize(term) in _normalize(title) for term in NON_SUBSTANTIVE)
        if non_substantive:
            decision, reason = "exclude", "duplicate_entity_or_release"
        elif scope and contribution:
            decision, reason = (
                "include",
                "public_metadata_explicitly_describes_in_scope_contribution",
            )
        else:
            decision, reason = "uncertain", "public_metadata_insufficient_for_final_eligibility"
        observations.append(
            {
                **base,
                "title": title,
                "canonical_url": canonical_url,
                "work_type": work_type,
                "scope_signal": scope,
                "contribution_signal": contribution,
                "decision": decision,
            }
        )
        resolutions.append(
            {
                "canonical_key": record["canonical_key"],
                "decision": decision,
                "reason": reason,
                "exclusion_reason": reason if decision == "exclude" else None,
                "evidence_sha256": evidence_hash,
            }
        )
    counts: dict[str, int] = {}
    for observation in observations:
        counts[observation["decision"]] = counts.get(observation["decision"], 0) + 1
    return {
        "workflow_version": "RBC-LAND-007-PENDING-PUBLIC-v0.1.0",
        "eligibility_input_sha256": "sha256:" + hashlib.sha256(eligibility_raw).hexdigest(),
        "observed_at_utc": observed_at_utc,
        "content_retention": (
            "minimal_metadata_and_hashes_only_no_abstract_description_body_or_full_text"
        ),
        "counts": dict(sorted(counts.items())),
        "observations": observations,
        "resolutions": resolutions,
        "limitations": [
            "Unreachable evidence remains pending, never excluded.",
            "Metadata decisions do not establish quality, novelty, or coverage.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("eligibility", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--base-resolutions", type=Path)
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    args = parser.parse_args()
    result = resolve(args.eligibility.read_bytes(), delay_seconds=args.delay_seconds)
    if args.base_resolutions:
        base = json.loads(args.base_resolutions.read_text(encoding="utf-8"))
        existing = {item["canonical_key"] for item in base["resolutions"]}
        overlap = existing.intersection(item["canonical_key"] for item in result["resolutions"])
        if overlap:
            raise ValueError(f"resolution overlaps base evidence: {sorted(overlap)}")
        result["base_resolutions_sha256"] = (
            "sha256:" + hashlib.sha256(args.base_resolutions.read_bytes()).hexdigest()
        )
        result["resolutions"] = [*base["resolutions"], *result["resolutions"]]
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
