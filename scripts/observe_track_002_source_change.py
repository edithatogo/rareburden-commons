#!/usr/bin/env python3
"""Run a bounded, fail-closed change exercise against Track 002 candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_ALLOWED_HOSTS = {
    "api.worldbank.org",
    "cdn.who.int",
    "population.un.org",
    "www.orphadata.com",
}
_RETRYABLE = {429, 502, 503, 504}
_MAX_BYTES = 60_000_000
_REQUIRED_ACTION = (
    "Keep activation disabled and repeat source, terms and methods disposition before "
    "registering changed or replacement bytes."
)


def _load_candidates(path: Path) -> list[dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if set(document) != {"schema_version", "candidates"} or document["schema_version"] != "1.0.0":
        raise ValueError("candidate configuration has an unexpected shape or version")
    candidates = document["candidates"]
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("candidate configuration must contain candidates")
    identifiers: set[str] = set()
    required = {"source_id", "release_id", "requested_url", "expected_sha256"}
    for candidate in candidates:
        if not isinstance(candidate, dict) or set(candidate) != required:
            raise ValueError("candidate has an unexpected shape")
        source_id = candidate["source_id"]
        if not isinstance(source_id, str) or not source_id or source_id in identifiers:
            raise ValueError("candidate source identifiers must be unique non-empty strings")
        identifiers.add(source_id)
        parsed = urllib.parse.urlsplit(str(candidate["requested_url"]))
        if (
            parsed.scheme != "https"
            or parsed.hostname not in _ALLOWED_HOSTS
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
        ):
            raise ValueError(f"untrusted candidate URL for {source_id}")
        expected = candidate["expected_sha256"]
        if not isinstance(expected, str) or len(expected) != 64:
            raise ValueError(f"invalid expected SHA-256 for {source_id}")
        try:
            int(expected, 16)
        except ValueError as exc:
            raise ValueError(f"invalid expected SHA-256 for {source_id}") from exc
    return candidates


def _read_bounded(response: Any) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    while chunk := response.read(64 * 1024):
        size += len(chunk)
        if size > _MAX_BYTES:
            raise ValueError("candidate response exceeded the 60 MB byte budget")
        digest.update(chunk)
    return size, digest.hexdigest()


def _failure_record(
    candidate: dict[str, Any], status: int | None, failure_reason: str
) -> dict[str, Any]:
    return {
        **candidate,
        "http_status": status,
        "bytes_observed": 0,
        "observed_sha256": None,
        "comparison": "unavailable",
        "failure_reason": failure_reason,
        "incident_required": True,
        "source_bytes_retained": False,
        "activation_permitted": False,
        "required_action": _REQUIRED_ACTION,
    }


def observe(
    source: Path,
    *,
    observed_at_utc: str | None = None,
    interval: float = 1.0,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    candidates = _load_candidates(source)
    observations: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        if index:
            time.sleep(max(interval, 0.0))
        request = urllib.request.Request(
            candidate["requested_url"],
            headers={"User-Agent": "rareburden-source-change-observer/1"},
        )
        for attempt in range(3):
            try:
                with opener(request, timeout=180) as response:
                    final_host = urllib.parse.urlsplit(response.geturl()).hostname
                    if final_host not in _ALLOWED_HOSTS:
                        raise ValueError("candidate redirected to an untrusted host")
                    size, digest = _read_bounded(response)
                    comparison = "stable" if digest == candidate["expected_sha256"] else "changed"
                    observations.append(
                        {
                            **candidate,
                            "http_status": response.status,
                            "bytes_observed": size,
                            "observed_sha256": digest,
                            "comparison": comparison,
                            "incident_required": comparison != "stable",
                            "source_bytes_retained": False,
                            "activation_permitted": False,
                            "required_action": None if comparison == "stable" else _REQUIRED_ACTION,
                        }
                    )
                break
            except urllib.error.HTTPError as exc:
                if exc.code in _RETRYABLE and attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue
                observations.append(_failure_record(candidate, exc.code, f"http_error_{exc.code}"))
                break
            except (urllib.error.URLError, TimeoutError, OSError):
                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue
                observations.append(_failure_record(candidate, None, "transport_unavailable"))
                break
            except ValueError as exc:
                observations.append(_failure_record(candidate, None, str(exc)))
                break

    counts = {
        state: sum(item["comparison"] == state for item in observations)
        for state in ("stable", "changed", "unavailable")
    }
    return {
        "schema_version": "1.0.0",
        "observed_at_utc": observed_at_utc or datetime.now(UTC).isoformat(),
        "status": "bounded_live_source_change_exercise",
        "activation_permitted": False,
        "pacing_seconds": interval,
        "max_response_bytes": _MAX_BYTES,
        "records": observations,
        "summary": counts,
        "claim_boundary": (
            "These are exact retrieval-time byte observations only. They do not establish "
            "publisher rights, scientific fitness, representativeness or production activation."
        ),
        "stop_conditions": [
            "changed or unavailable bytes",
            "untrusted redirect",
            "response over byte budget",
            "terms, release identity or intended-use drift",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--observed-at-utc")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    result = observe(
        args.source,
        observed_at_utc=args.observed_at_utc,
        interval=args.interval,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
