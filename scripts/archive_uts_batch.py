#!/usr/bin/env python3
"""Archive a bounded authenticated UTS release batch to a private Hub dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, cast

_SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9._+-]+$")
_DOWNLOAD_ENDPOINT = "https://uts-ws.nlm.nih.gov/download"
_REQUEST_INTERVAL_SECONDS = 2.0
_RETRYABLE_STATUS = {429, 502, 503, 504}


def _retry_delay(headers: Any, attempt: int) -> int:
    retry_after = headers.get("Retry-After") if headers is not None else None
    if retry_after and str(retry_after).isdigit():
        retry_seconds = int(str(retry_after))
        return min(max(retry_seconds, 2), 900)
    return min(2 << max(attempt, 0), 300)


def _load_family(manifest: Path, release_type: str) -> list[dict[str, Any]]:
    document = json.loads(manifest.read_text(encoding="utf-8"))
    families = document.get("families") if isinstance(document, dict) else None
    if not isinstance(families, list):
        raise ValueError("UTS manifest families must be an array")
    matches = [item for item in families if item.get("release_type") == release_type]
    if len(matches) != 1 or not isinstance(matches[0].get("releases"), list):
        raise ValueError(f"unknown or duplicate UTS release family: {release_type}")
    releases = matches[0]["releases"]
    for index, release in enumerate(releases):
        required = {
            "fileName",
            "releaseVersion",
            "releaseDate",
            "downloadUrl",
            "releaseType",
            "product",
        }
        allowed = required | {"current"}
        if (
            not isinstance(release, dict)
            or not required.issubset(release)
            or not set(release).issubset(allowed)
            or ("current" in release and not isinstance(release["current"], bool))
        ):
            raise ValueError(f"release {index} has an unexpected shape")
        for field in ("fileName", "releaseVersion"):
            if not _SAFE_COMPONENT.fullmatch(str(release[field])):
                raise ValueError(f"release {index} has unsafe {field}")
        if not str(release["downloadUrl"]).startswith("https://download.nlm.nih.gov/"):
            raise ValueError(f"release {index} has an untrusted download URL")
    return cast(list[dict[str, Any]], releases)


def _download(
    release: dict[str, Any], destination: Path, api_key: str, remaining_bytes: int
) -> tuple[int, str]:
    query = urllib.parse.urlencode({"url": release["downloadUrl"], "apiKey": api_key})
    request = urllib.request.Request(
        f"{_DOWNLOAD_ENDPOINT}?{query}",
        headers={"User-Agent": "rareburden-licensed-archive/1"},
    )
    for attempt in range(6):
        digest = hashlib.sha256()
        total = 0
        try:
            with (
                urllib.request.urlopen(request, timeout=180) as response,
                destination.open("wb") as output,
            ):
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > remaining_bytes:
                        raise ValueError("UTS batch exceeded the configured byte budget")
                    output.write(chunk)
                    digest.update(chunk)
            return total, digest.hexdigest()
        except urllib.error.HTTPError as error:
            destination.unlink(missing_ok=True)
            if error.code not in _RETRYABLE_STATUS or attempt == 5:
                raise RuntimeError(
                    f"authenticated download failed for {release['fileName']}"
                ) from None
            time.sleep(_retry_delay(error.headers, attempt))
        except (urllib.error.URLError, TimeoutError):
            destination.unlink(missing_ok=True)
            if attempt == 5:
                raise RuntimeError(
                    f"authenticated download failed for {release['fileName']}"
                ) from None
            time.sleep(_retry_delay(None, attempt))
    raise RuntimeError("UTS download retry loop exhausted")  # pragma: no cover


def archive_uts_batch(
    manifest: Path,
    release_type: str,
    repo_id: str,
    *,
    start: int,
    count: int,
    max_bytes: int,
) -> dict[str, Any]:
    from huggingface_hub import HfApi  # type: ignore[import-not-found]
    from huggingface_hub.errors import HfHubHTTPError  # type: ignore[import-not-found]

    api_key = os.environ.get("UMLS_API_KEY")
    token = os.environ.get("HF_TOKEN")
    if not api_key or not token:
        raise RuntimeError("UMLS_API_KEY and HF_TOKEN are required")
    releases = _load_family(manifest, release_type)[start : start + count]
    if not releases:
        raise ValueError("selected UTS batch is empty")

    api = HfApi(token=token)
    destination_info = api.dataset_info(repo_id, files_metadata=True)
    if not destination_info.private:
        raise RuntimeError("destination dataset must be private")

    observed: list[dict[str, Any]] = []
    used_bytes = 0
    with tempfile.TemporaryDirectory(prefix="rareburden-uts-") as temporary:
        root = Path(temporary)
        for offset, release in enumerate(releases, start=start):
            if observed:
                time.sleep(_REQUEST_INTERVAL_SECONDS)
            relative = Path(
                "licensed-private",
                "uts",
                release_type,
                str(release["releaseVersion"]),
                str(release["fileName"]),
            )
            local = root / relative
            local.parent.mkdir(parents=True, exist_ok=True)
            size, digest = _download(release, local, api_key, max_bytes - used_bytes)
            used_bytes += size
            observed.append(
                {
                    "index": offset,
                    "release_type": release_type,
                    "release_version": release["releaseVersion"],
                    "release_date": release["releaseDate"],
                    "file_name": release["fileName"],
                    "source_url": release["downloadUrl"],
                    "archive_path": relative.as_posix(),
                    "bytes": size,
                    "sha256": digest,
                }
            )

        receipt_path = Path(
            "manifests",
            "uts",
            "receipts",
            release_type,
            f"{start:05d}-{start + len(observed) - 1:05d}.json",
        )
        local_receipt = root / receipt_path
        local_receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt = {
            "schema_version": "1.0",
            "status": "private_licensed_archive_only",
            "release_type": release_type,
            "start": start,
            "count": len(observed),
            "bytes": used_bytes,
            "artifacts": observed,
            "claims": {
                "public_redistribution": False,
                "clinical_validation": False,
                "production_activation": False,
            },
        }
        local_receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        for attempt in range(12):
            try:
                commit = api.upload_folder(
                    folder_path=root,
                    repo_id=repo_id,
                    repo_type="dataset",
                    commit_message=f"Archive UTS {release_type} {start}:{start + len(observed)}",
                )
                break
            except HfHubHTTPError as error:
                if error.response.status_code != 429 or attempt == 11:
                    raise
                time.sleep(_retry_delay(error.response.headers, attempt))
        else:  # pragma: no cover
            raise RuntimeError("Hugging Face upload retry loop exhausted")

    remote = api.dataset_info(repo_id, files_metadata=True)
    remote_files = {item.rfilename: item.size for item in remote.siblings}
    for artifact in observed:
        if remote_files.get(artifact["archive_path"]) != artifact["bytes"]:
            raise RuntimeError(f"remote verification failed for {artifact['archive_path']}")
    if receipt_path.as_posix() not in remote_files:
        raise RuntimeError("remote receipt verification failed")
    receipt["commit"] = str(commit)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--release-type", required=True)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--max-bytes", type=int, default=8_000_000_000)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = archive_uts_batch(
        args.manifest,
        args.release_type,
        args.repo_id,
        start=args.start,
        count=args.count,
        max_bytes=args.max_bytes,
    )
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
