#!/usr/bin/env python3
"""Archive an explicitly authorized, bounded MedDRA or MLDS batch privately."""

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
from pathlib import Path
from typing import Any, cast

DESTINATION = "edithatogo/hpo-licensed-ontology-archive"
ALLOWED_HOSTS = {
    "www.meddra.org",
    "files.meddra.org",
    "alt.meddra.org",
    "mlds.ihtsdotools.org",
}
MAX_ARTIFACTS = 3
MAX_BYTES = 8_000_000_000


def canonical_sha256(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def load_inventory(path: Path) -> dict[str, Any]:
    from jsonschema import Draft202012Validator, ValidationError

    value = json.loads(path.read_text(encoding="utf-8"))
    schema_path = (
        Path(__file__).resolve().parents[1] / "schemas/licensed-portal-inventory.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        Draft202012Validator(schema).validate(value)
    except ValidationError as error:
        raise ValueError(f"inventory violates schema: {error.message}") from None
    if value.get("schema_version") != "1.0" or value.get("portal") not in {"meddra", "mlds"}:
        raise ValueError("inventory schema version or portal is unsupported")
    if value.get("destination") != DESTINATION:
        raise ValueError("licensed destination must be the canonical private archive")
    terms = value.get("terms", {})
    if terms.get("cloud_storage_decision") != "permit_private_cloud":
        raise ValueError("exact terms do not permit private cloud storage")
    if not terms.get("decision_evidence"):
        raise ValueError("cloud-storage permission requires decision evidence")
    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("inventory artifacts must be a list")
    seen: set[tuple[str, str]] = set()
    for item in artifacts:
        key = (str(item.get("archive_path")), str(item.get("sha256")))
        if key in seen:
            raise ValueError("inventory contains a duplicate artifact")
        seen.add(key)
        path_value = Path(key[0])
        prefix = (
            "licensed-private/meddra"
            if value["portal"] == "meddra"
            else "licensed-private/snomed-ct"
        )
        if (
            path_value.is_absolute()
            or ".." in path_value.parts
            or not key[0].startswith(prefix + "/")
        ):
            raise ValueError("artifact archive path is unsafe or belongs to another portal")
        if len(key[1]) != 64 or any(char not in "0123456789abcdef" for char in key[1]):
            raise ValueError("artifact SHA-256 is invalid")
        if not isinstance(item.get("bytes"), int) or item["bytes"] < 1:
            raise ValueError("artifact byte count is invalid")
        state = item.get("access_state")
        if state == "approved_download":
            url = str(item.get("download_url") or "")
            if urllib.parse.urlsplit(url).scheme != "https":
                raise ValueError("approved downloads require an exact HTTPS URL")
            if urllib.parse.urlsplit(url).hostname not in ALLOWED_HOSTS:
                raise ValueError("download host is not an approved official portal host")
        elif state == "already_archived":
            if not item.get("duplicate_of"):
                raise ValueError("already_archived artifacts require an exact duplicate reference")
        else:
            raise ValueError("metadata-only artifacts cannot enter an archive batch")
    return cast(dict[str, Any], value)


class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    """Prevent credentials being forwarded to a different host."""

    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> Any:
        if urllib.parse.urlsplit(req.full_url).hostname != urllib.parse.urlsplit(newurl).hostname:
            raise RuntimeError("licensed download attempted a cross-host redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(item: dict[str, Any], destination: Path, *, authorization: str) -> None:
    request = urllib.request.Request(
        item["download_url"],
        headers={"User-Agent": "rareburden-licensed-archive/1", "Authorization": authorization},
    )
    opener = urllib.request.build_opener(SameHostRedirect())
    digest = hashlib.sha256()
    total = 0
    try:
        with opener.open(request, timeout=180) as response, destination.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > item["bytes"] or total > MAX_BYTES:
                    raise ValueError("licensed download exceeded exact byte budget")
                digest.update(chunk)
                output.write(chunk)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"licensed portal returned HTTP {error.code}") from None
    if total != item["bytes"] or digest.hexdigest() != item["sha256"]:
        raise ValueError("licensed download did not match exact size and SHA-256")


def archive_batch(
    inventory_path: Path, *, start: int, count: int, max_bytes: int
) -> dict[str, Any]:
    from huggingface_hub import HfApi  # type: ignore[import-not-found]

    if count < 1 or count > MAX_ARTIFACTS or max_bytes < 1 or max_bytes > MAX_BYTES:
        raise ValueError("batch artifact or byte budget exceeds policy")
    inventory = load_inventory(inventory_path)
    selected = inventory["artifacts"][start : start + count]
    if not selected:
        raise ValueError("selected licensed batch is empty")
    if (
        sum(item["bytes"] for item in selected if item["access_state"] == "approved_download")
        > max_bytes
    ):
        raise ValueError("selected licensed batch exceeds byte budget")
    token = os.environ.get("HF_TOKEN")
    authorization = os.environ.get("PORTAL_AUTHORIZATION")
    if not token:
        raise RuntimeError("HF_TOKEN is required")
    if any(item["access_state"] == "approved_download" for item in selected) and not authorization:
        raise RuntimeError("PORTAL_AUTHORIZATION is required for approved downloads")
    api = HfApi(token=token)
    info = api.dataset_info(DESTINATION, files_metadata=True)
    if not info.private:
        raise RuntimeError("licensed archive destination must remain private")
    remote_files = {entry.rfilename: entry.size for entry in info.siblings}
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="rareburden-licensed-") as temporary:
        root = Path(temporary)
        downloads = 0
        for index, item in enumerate(selected, start=start):
            result = {
                "index": index,
                "status": "referenced_existing"
                if item["access_state"] == "already_archived"
                else "archived",
                "archive_path": item["archive_path"],
                "bytes": item["bytes"],
                "sha256": item["sha256"],
                "duplicate_of": item["duplicate_of"],
            }
            if item["access_state"] == "already_archived":
                if remote_files.get(item["duplicate_of"]) != item["bytes"]:
                    raise RuntimeError(
                        "duplicate reference is absent or has a different remote size"
                    )
            else:
                if downloads:
                    time.sleep(2.0)
                target = root / item["archive_path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                download(item, target, authorization=authorization or "")
                downloads += 1
            results.append(result)
        if downloads:
            message = f"Archive authorized {inventory['portal']} batch {start}:{start + count}"
            api.upload_folder(
                folder_path=root,
                repo_id=DESTINATION,
                repo_type="dataset",
                commit_message=message,
            )
    refreshed = api.dataset_info(DESTINATION, files_metadata=True)
    refreshed_files = {entry.rfilename: entry.size for entry in refreshed.siblings}
    for result in results:
        check_path = result["duplicate_of"] or result["archive_path"]
        if refreshed_files.get(check_path) != result["bytes"]:
            raise RuntimeError("remote archive verification failed")
    manifest_digest = canonical_sha256(inventory)
    receipt_path = f"licensed-private/receipts/{inventory['portal']}/{manifest_digest}.json"
    receipt = {
        "schema_version": "1.0",
        "portal": inventory["portal"],
        "destination": DESTINATION,
        "visibility": "private",
        "manifest_sha256": manifest_digest,
        "receipt_path": receipt_path,
        "results": results,
        "claims": {
            "public_redistribution": False,
            "portal_completeness": False,
            "native_edition_completeness": False,
            "production_activation": False,
        },
    }
    receipt_bytes = (json.dumps(receipt, indent=2) + "\n").encode()
    api.upload_file(
        path_or_fileobj=receipt_bytes,
        path_in_repo=receipt_path,
        repo_id=DESTINATION,
        repo_type="dataset",
        commit_message=f"Record authorized {inventory['portal']} archive receipt",
    )
    receipt_info = api.dataset_info(DESTINATION, files_metadata=True)
    receipt_files = {entry.rfilename: entry.size for entry in receipt_info.siblings}
    if receipt_files.get(receipt_path) != len(receipt_bytes):
        raise RuntimeError("remote licensed receipt verification failed")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--max-bytes", type=int, default=1_000_000_000)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = archive_batch(
        args.inventory, start=args.start, count=args.count, max_bytes=args.max_bytes
    )
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
