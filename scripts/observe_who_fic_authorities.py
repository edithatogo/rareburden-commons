#!/usr/bin/env python3
"""Hash official authority landing pages without retaining response bodies."""

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
    "www.who.int",
    "www.cdc.gov",
    "www.ihacpa.gov.au",
    "www.cihi.ca",
    "www.bfarm.de",
    "classbrowser.nhs.uk",
    "www.rivm.nl",
    "www.socialstyrelsen.se",
    "www.health.govt.nz",
}
_RETRYABLE = {429, 502, 503, 504}
_MAX_BYTES = 4_000_000


def _validate_source(document: dict[str, Any]) -> list[dict[str, Any]]:
    allowed_top = {
        "schema_version",
        "as_of",
        "status",
        "publication_route",
        "scope_statement",
        "who_fic",
        "national_authorities",
        "limitations",
    }
    if set(document) != allowed_top:
        raise ValueError("authority source ledger has unexpected top-level fields")
    records = document.get("who_fic", []) + document.get("national_authorities", [])
    if not isinstance(records, list) or not records:
        raise ValueError("authority source ledger has no records")
    ids: set[str] = set()
    required = {
        "id",
        "classification",
        "country_or_area",
        "languages",
        "version_or_release",
        "authority",
        "source_url",
        "terms_state",
        "artifact_route",
    }
    for record in records:
        if not isinstance(record, dict) or set(record) != required:
            raise ValueError("authority record has an unexpected shape")
        if record["id"] in ids:
            raise ValueError("authority record identifiers must be unique")
        ids.add(record["id"])
        parsed = urllib.parse.urlsplit(str(record["source_url"]))
        if (
            parsed.scheme != "https"
            or parsed.hostname not in _ALLOWED_HOSTS
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
        ):
            raise ValueError(f"untrusted authority source URL for {record['id']}")
        if not isinstance(record["languages"], list) or not record["languages"]:
            raise ValueError(f"authority record {record['id']} has no language state")
        if record["artifact_route"] not in {
            "metadata_only",
            "private_or_metadata_only",
            "metadata_only_pending_file_level_disposition",
            "metadata_only_or_private_if_licence_permits",
            "metadata_only_or_private_if_product_terms_permit",
            "metadata_only_pending_contract_disposition",
            "metadata_only_portal_access_required_for_datafiles",
            "metadata_only_pending_exact_edition_terms",
        }:
            raise ValueError(f"authority record {record['id']} has unsafe archive route")
    return records


def _delay(headers: Any, attempt: int) -> int:
    retry_after = headers.get("Retry-After") if headers is not None else None
    if retry_after and str(retry_after).isdigit():
        return min(max(int(str(retry_after)), 2), 900)
    return min(2 << max(attempt, 0), 300)


def _read_bounded(response: Any) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    while chunk := response.read(64 * 1024):
        size += len(chunk)
        if size > _MAX_BYTES:
            raise ValueError("authority landing page exceeded byte budget")
        digest.update(chunk)
    return size, digest.hexdigest()


def observe(
    source: Path,
    *,
    interval: float = 2.0,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    document = json.loads(source.read_text(encoding="utf-8"))
    records = _validate_source(document)
    observations: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if index:
            time.sleep(max(interval, 0.0))
        request = urllib.request.Request(
            record["source_url"],
            headers={"User-Agent": "rareburden-official-source-observer/1"},
        )
        for attempt in range(5):
            try:
                with opener(request, timeout=60) as response:
                    final_url = response.geturl()
                    final_host = urllib.parse.urlsplit(final_url).hostname
                    if final_host not in _ALLOWED_HOSTS:
                        raise ValueError("authority source redirected to an untrusted host")
                    size, digest = _read_bounded(response)
                    observations.append(
                        {
                            "id": record["id"],
                            "source_url": record["source_url"],
                            "final_url": final_url,
                            "http_status": response.status,
                            "content_type": response.headers.get("Content-Type", ""),
                            "bytes_observed": size,
                            "sha256": digest,
                            "body_retained": False,
                        }
                    )
                break
            except urllib.error.HTTPError as error:
                if error.code not in _RETRYABLE or attempt == 4:
                    observations.append(
                        {
                            "id": record["id"],
                            "source_url": record["source_url"],
                            "final_url": error.geturl(),
                            "http_status": error.code,
                            "content_type": error.headers.get("Content-Type", ""),
                            "bytes_observed": 0,
                            "sha256": None,
                            "body_retained": False,
                        }
                    )
                    break
                time.sleep(_delay(error.headers, attempt))
            except (urllib.error.URLError, TimeoutError):
                if attempt == 4:
                    observations.append(
                        {
                            "id": record["id"],
                            "source_url": record["source_url"],
                            "final_url": None,
                            "http_status": None,
                            "content_type": None,
                            "bytes_observed": 0,
                            "sha256": None,
                            "body_retained": False,
                        }
                    )
                    break
                time.sleep(_delay(None, attempt))
    return {
        "schema_version": "1.0",
        "observed_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "source_manifest": source.as_posix(),
        "source_manifest_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "status": "bounded_official_landing_page_observation",
        "observations": observations,
        "claims": {
            "global_completeness": False,
            "language_completeness": False,
            "artifact_rights": False,
            "source_bytes_archived": False,
            "production_activation": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    result = observe(args.source, interval=args.interval)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
