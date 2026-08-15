#!/usr/bin/env python3
"""Inventory WHO ICD API releases and preserve raw observations privately.

The checked-in output is metadata only. Authenticated API response bytes are
uploaded only to a verified private Hugging Face dataset when a destination is
provided, then discarded with the runner temporary directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_TOKEN_HOST = "icdaccessmanagement.who.int"
_API_HOST = "id.who.int"
_DEFAULT_TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
_DEFAULT_API_BASE = "https://id.who.int"
_RETRYABLE_STATUS = {429, 502, 503, 504}


def _trusted_url(value: str, *, host: str, path_prefix: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if (
        parsed.scheme != "https"
        or parsed.hostname != host
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or not (parsed.path or "/").startswith(path_prefix)
    ):
        raise ValueError(f"untrusted WHO endpoint for {host}")
    return value.rstrip("/")


def _retry_delay(headers: Any, attempt: int) -> int:
    retry_after = headers.get("Retry-After") if headers is not None else None
    if retry_after and str(retry_after).isdigit():
        return min(max(int(str(retry_after)), 2), 900)
    return min(2 << max(attempt, 0), 300)


@dataclass(frozen=True)
class Observation:
    endpoint: str
    language: str
    status: int
    size: int
    sha256: str
    payload: bytes


class ICDClient:
    """Small rate-limited WHO ICD API v2 client."""

    def __init__(
        self,
        *,
        token_url: str,
        api_base: str,
        client_id: str,
        client_secret: str,
        request_interval: float = 2.0,
    ) -> None:
        self.token_url = _trusted_url(token_url, host=_TOKEN_HOST, path_prefix="/connect/token")
        self.api_base = _trusted_url(api_base, host=_API_HOST, path_prefix="/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.request_interval = max(request_interval, 0.0)
        self._token: str | None = None
        self._last_request: float | None = None

    def _authenticate(self) -> str:
        body = urllib.parse.urlencode(
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "icdapi_access",
                "grant_type": "client_credentials",
            }
        ).encode()
        request = urllib.request.Request(
            self.token_url,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            document = json.loads(response.read())
        token = document.get("access_token") if isinstance(document, dict) else None
        if not isinstance(token, str) or not token:
            raise RuntimeError("WHO token endpoint returned no access token")
        self._token = token
        return token

    def _wait(self) -> None:
        if self._last_request is None:
            return
        remaining = self.request_interval - (time.monotonic() - self._last_request)
        if remaining > 0:
            time.sleep(remaining)

    def get(self, endpoint: str, *, language: str = "en") -> Observation:
        if not endpoint.startswith("/icd/") or ".." in endpoint:
            raise ValueError("WHO API endpoint must be an /icd/ path")
        token = self._token or self._authenticate()
        url = _trusted_url(f"{self.api_base}{endpoint}", host=_API_HOST, path_prefix="/icd/")
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "API-Version": "v2",
                "Accept": "application/json",
                "Accept-Language": language,
                "User-Agent": "rareburden-who-icd-inventory/1",
            },
        )
        for attempt in range(6):
            self._wait()
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    payload = response.read()
                    status = response.status
                self._last_request = time.monotonic()
                return Observation(
                    endpoint=endpoint,
                    language=language,
                    status=status,
                    size=len(payload),
                    sha256=hashlib.sha256(payload).hexdigest(),
                    payload=payload,
                )
            except urllib.error.HTTPError as error:
                self._last_request = time.monotonic()
                if error.code == 404:
                    payload = error.read()
                    return Observation(
                        endpoint=endpoint,
                        language=language,
                        status=404,
                        size=len(payload),
                        sha256=hashlib.sha256(payload).hexdigest(),
                        payload=payload,
                    )
                if error.code not in _RETRYABLE_STATUS or attempt == 5:
                    raise RuntimeError(
                        f"WHO ICD API request failed with HTTP {error.code}"
                    ) from None
                time.sleep(_retry_delay(error.headers, attempt))
            except (urllib.error.URLError, TimeoutError):
                self._last_request = time.monotonic()
                if attempt == 5:
                    raise RuntimeError("WHO ICD API request failed after retries") from None
                time.sleep(_retry_delay(None, attempt))
        raise RuntimeError("WHO ICD API retry loop exhausted")  # pragma: no cover


def _document(observation: Observation) -> dict[str, Any]:
    try:
        value = json.loads(observation.payload)
    except json.JSONDecodeError as error:
        raise RuntimeError("WHO ICD API returned non-JSON content") from error
    if not isinstance(value, dict):
        raise RuntimeError("WHO ICD API returned a non-object document")
    return value


def _release_ids(document: dict[str, Any]) -> list[str]:
    releases: list[str] = []
    current = document.get("releaseId")
    if isinstance(current, str) and current:
        releases.append(current)
    for value in document.get("allReleases", []):
        if not isinstance(value, str):
            continue
        version = urllib.parse.parse_qs(urllib.parse.urlsplit(value).query).get("version")
        if version and version[0] not in releases:
            releases.append(version[0])
    return releases


def _observation_record(observation: Observation) -> dict[str, Any]:
    return {
        "endpoint": observation.endpoint,
        "language": observation.language,
        "http_status": observation.status,
        "bytes": observation.size,
        "sha256": observation.sha256,
        "raw_route": "private_licensed_archive_only",
    }


def enumerate_inventory(
    client: ICDClient, *, observed_at: str
) -> tuple[dict[str, Any], list[Observation]]:
    """Return a fail-closed release/language matrix and exact observations."""
    observations: list[Observation] = []
    foundation_observation = client.get("/icd/entity")
    observations.append(foundation_observation)
    foundation = _document(foundation_observation)

    foundation_languages = foundation.get("availableLanguages", [])
    if not isinstance(foundation_languages, list) or not all(
        isinstance(item, str) and item for item in foundation_languages
    ):
        raise RuntimeError("WHO Foundation endpoint omitted availableLanguages")
    classifications: list[dict[str, Any]] = [
        {
            "classification": "who-fic-foundation",
            "release_id": foundation.get("releaseId"),
            "endpoint": foundation_observation.endpoint,
            "http_status": foundation_observation.status,
            "available_languages": sorted(set(foundation_languages)),
            "language_evidence": "union_across_current_api_classifications",
            "release_date": foundation.get("releaseDate"),
            "observation_sha256": foundation_observation.sha256,
        }
    ]
    for release_id in _release_ids(foundation):
        for linearization in ("mms", "icf"):
            observation = client.get(f"/icd/release/11/{release_id}/{linearization}")
            observations.append(observation)
            record: dict[str, Any] = {
                "classification": f"icd11-{linearization}",
                "release_id": release_id,
                "endpoint": observation.endpoint,
                "http_status": observation.status,
                "available_languages": [],
                "prerelease_languages": [],
                "release_date": None,
                "observation_sha256": observation.sha256,
            }
            if observation.status == 200:
                document = _document(observation)
                languages = document.get("availableLanguages", [])
                prerelease = document.get("prereleaseLanguages", [])
                if not isinstance(languages, list) or not all(
                    isinstance(item, str) and item for item in languages
                ):
                    raise RuntimeError("WHO linearization omitted availableLanguages")
                if not isinstance(prerelease, list):
                    raise RuntimeError("WHO linearization prereleaseLanguages is invalid")
                record.update(
                    {
                        "available_languages": sorted(set(languages)),
                        "prerelease_languages": sorted(set(prerelease)),
                        "release_date": document.get("releaseDate"),
                    }
                )
            classifications.append(record)

    icd10_top_observation = client.get("/icd/release/10")
    observations.append(icd10_top_observation)
    icd10_top = _document(icd10_top_observation)
    release_urls = icd10_top.get("release")
    if not isinstance(release_urls, list) or not release_urls:
        raise RuntimeError("WHO ICD-10 endpoint returned no releases")
    for release_url in release_urls:
        if not isinstance(release_url, str):
            raise RuntimeError("WHO ICD-10 release URI is invalid")
        parsed = urllib.parse.urlsplit(release_url)
        if parsed.hostname != _API_HOST or not parsed.path.startswith("/icd/release/10/"):
            raise RuntimeError("WHO ICD-10 release URI is untrusted")
        observation = client.get(parsed.path)
        observations.append(observation)
        document = _document(observation)
        classifications.append(
            {
                "classification": "icd10",
                "release_id": parsed.path.rsplit("/", 1)[-1],
                "endpoint": parsed.path,
                "http_status": observation.status,
                "available_languages": [],
                "language_evidence": "not_exposed_by_release_endpoint",
                "release_date": document.get("releaseDate"),
                "observation_sha256": observation.sha256,
            }
        )

    inventory = {
        "schema_version": "1.0",
        "observed_at": observed_at,
        "source": "https://id.who.int",
        "api_version": "v2",
        "scope": ["who-fic-foundation", "icd11-mms", "icf", "icd10"],
        "classifications": classifications,
        "observations": [_observation_record(item) for item in observations],
        "rights": {
            "public_manifest": "metadata_hashes_only",
            "raw_api_responses": "private_licensed_archive_only",
            "public_raw_redistribution": False,
        },
        "claims": {
            "complete_api_graph": False,
            "complete_who_fic_family": False,
            "national_editions_included": False,
            "production_activation": False,
        },
        "known_gaps": [
            "ICD-10 release endpoints do not expose an availableLanguages field",
            "ICHI and other WHO derived or related classifications are outside "
            "the observed ICD API scope",
            "national modifications require separate country-authority release inventories",
        ],
    }
    return inventory, observations


def _archive_private(
    *,
    observations: list[Observation],
    inventory: dict[str, Any],
    repo_id: str,
) -> str:
    from huggingface_hub import HfApi  # type: ignore[import-not-found]

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required for private archival")
    api = HfApi(token=token)
    info = api.dataset_info(repo_id, files_metadata=True)
    if not info.private:
        raise RuntimeError("WHO raw observation destination must be private")
    stamp = str(inventory["observed_at"]).replace(":", "-")
    expected: dict[str, int] = {}
    with tempfile.TemporaryDirectory(prefix="rareburden-who-icd-") as temporary:
        root = Path(temporary)
        for index, observation in enumerate(observations):
            path = root / "licensed-private" / "who-icd" / stamp / f"{index:03d}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(observation.payload)
            expected[path.relative_to(root).as_posix()] = observation.size
        manifest = root / "licensed-private" / "who-icd" / stamp / "manifest.json"
        manifest.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
        expected[manifest.relative_to(root).as_posix()] = manifest.stat().st_size
        commit = api.upload_folder(
            folder_path=root,
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"Archive WHO ICD API observations {inventory['observed_at']}",
        )
    remote = api.dataset_info(repo_id, files_metadata=True)
    remote_sizes = {item.rfilename: item.size for item in remote.siblings}
    for remote_path, size in expected.items():
        if remote_sizes.get(remote_path) != size:
            raise RuntimeError(f"private WHO archive verification failed for {remote_path}")
    return str(commit)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--private-repo-id")
    parser.add_argument("--request-interval", type=float, default=2.0)
    args = parser.parse_args()
    required = {
        name: os.environ.get(name)
        for name in (
            "WHO_ICD_CLIENT_ID",
            "WHO_ICD_CLIENT_SECRET",
            "WHO_ICD_TOKEN_URL",
            "WHO_ICD_API_BASE_URL",
        )
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"missing required environment variables: {', '.join(missing)}")
    client = ICDClient(
        token_url=str(required["WHO_ICD_TOKEN_URL"]),
        api_base=str(required["WHO_ICD_API_BASE_URL"]),
        client_id=str(required["WHO_ICD_CLIENT_ID"]),
        client_secret=str(required["WHO_ICD_CLIENT_SECRET"]),
        request_interval=args.request_interval,
    )
    observed_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    inventory, observations = enumerate_inventory(client, observed_at=observed_at)
    if args.private_repo_id:
        inventory["private_archive_commit"] = _archive_private(
            observations=observations,
            inventory=inventory,
            repo_id=args.private_repo_id,
        )
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
