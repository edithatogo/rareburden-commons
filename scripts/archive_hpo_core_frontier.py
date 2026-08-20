#!/usr/bin/env python3
"""Archive a bounded, exact HPO core-ontology batch to the public HF archive."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

_DESTINATION = "edithatogo/rareburden-commons-open-source-snapshots"
_PUBLIC_ROUTE = "public_exact_unmodified_with_official_conditions"


def load_candidates(matrix_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    candidates = [item for item in payload["assets"] if item["archive_route"] == _PUBLIC_ROUTE]
    candidates.sort(key=lambda item: (item["release_tag"], item["name"]))
    keys = [(item["release_tag"], item["name"]) for item in candidates]
    if len(keys) != len(set(keys)):
        raise ValueError("HPO core archive candidates contain duplicate release/name keys")
    for item in candidates:
        parsed = urllib.parse.urlsplit(item["browser_download_url"])
        if parsed.scheme != "https" or parsed.hostname != "github.com":
            raise ValueError("HPO source URL must be an official GitHub HTTPS release URL")
        if not set(item["conditions"]) >= {
            "preserve_exact_bytes",
            "include_release_tag",
            "acknowledge_and_cite_HPO_Consortium",
        }:
            raise ValueError("HPO public candidate is missing mandatory licence conditions")
    return candidates


def staging_path(root: Path, item: dict[str, Any]) -> Path:
    """Return a collision-free local path for one release asset."""
    release_tag = str(item["release_tag"])
    name = str(item["name"])
    if Path(release_tag).name != release_tag or Path(name).name != name:
        raise ValueError("HPO release tag and asset name must be plain path components")
    return root / release_tag / name


def archive_batch(matrix_path: Path, *, start: int, count: int, max_bytes: int) -> dict[str, Any]:
    from huggingface_hub import CommitOperationAdd, HfApi  # type: ignore[import-not-found]

    if start < 0 or count < 1 or count > 10 or max_bytes < 1 or max_bytes > 1_000_000_000:
        raise ValueError("HPO batch exceeds the bounded run policy")
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required")
    candidates = load_candidates(matrix_path)
    selected = candidates[start : start + count]
    if not selected:
        raise ValueError("selected HPO core batch is empty")
    api = HfApi(token=token)
    info = api.dataset_info(_DESTINATION, files_metadata=True)
    if info.private:
        raise RuntimeError("HPO core destination must be public")
    remote = {item.rfilename: item.size for item in info.siblings}
    results: list[dict[str, Any]] = []
    operations: list[Any] = []
    used = 0
    with tempfile.TemporaryDirectory(prefix="rareburden-hpo-core-") as temporary:
        root = Path(temporary)
        for item in selected:
            destination = f"hpo/releases/{item['release_tag']}/{item['name']}"
            if destination in remote:
                if remote[destination] != item["size"]:
                    raise RuntimeError(f"remote size conflicts with manifest: {destination}")
                results.append(
                    {"path": destination, "status": "already_present", "bytes": remote[destination]}
                )
                continue
            if results:
                time.sleep(2)
            request = urllib.request.Request(
                item["browser_download_url"], headers={"User-Agent": "rareburden-archive/1"}
            )
            local = staging_path(root, item)
            local.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            size = 0
            with (
                urllib.request.urlopen(request, timeout=180) as response,
                local.open("wb") as output,
            ):
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    used += len(chunk)
                    if used > max_bytes:
                        raise ValueError("HPO batch exceeded byte budget")
                    digest.update(chunk)
                    output.write(chunk)
            if size != item["size"]:
                raise RuntimeError(f"source size drifted: {item['release_tag']}/{item['name']}")
            sha256 = digest.hexdigest()
            expected = item.get("digest")
            if expected and expected != f"sha256:{sha256}":
                raise RuntimeError("source digest differs from GitHub release metadata")
            operations.append(
                CommitOperationAdd(
                    path_or_fileobj=str(local),
                    path_in_repo=destination,
                )
            )
            results.append(
                {
                    "path": destination,
                    "status": "uploaded",
                    "bytes": size,
                    "sha256": sha256,
                }
            )
        receipt = {
            "schema_version": "1.0",
            "status": "bounded_public_exact_unmodified_archive",
            "repository": _DESTINATION,
            "start": start,
            "requested_count": count,
            "used_bytes": used,
            "results": results,
            "commit_mode": "single_atomic_batch_commit",
            "attribution": "Human Phenotype Ontology Consortium",
            "licence_evidence": "https://human-phenotype-ontology.github.io/license.html",
            "modification": "none; exact publisher release bytes",
            "claims": {
                "clinical_validation": False,
                "third_party_terms_cleared": False,
                "all_history_complete": False,
            },
        }
        receipt_path = f"hpo/receipts/batch-{start:04d}-{start + len(selected) - 1:04d}.json"
        operations.append(
            CommitOperationAdd(
                path_or_fileobj=io.BytesIO((json.dumps(receipt, sort_keys=True) + "\n").encode()),
                path_in_repo=receipt_path,
            )
        )
        commit = api.create_commit(
            repo_id=_DESTINATION,
            repo_type="dataset",
            operations=operations,
            commit_message=f"Archive bounded HPO core batch {start}:{start + len(selected)}",
            commit_description=(
                "Upload exact rights-cleared objects and their receipt in one atomic commit "
                "to respect the free-tier repository commit limit."
            ),
        )
        receipt["commit"] = str(commit)
    verified = {
        item.rfilename: item.size
        for item in api.dataset_info(_DESTINATION, files_metadata=True).siblings
    }
    for result in results:
        if verified.get(result["path"]) != result["bytes"]:
            raise RuntimeError(f"remote verification failed: {result['path']}")
    if receipt_path not in verified:
        raise RuntimeError("remote HPO batch receipt is missing")
    receipt["remote_receipt_path"] = receipt_path
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--max-bytes", type=int, default=500_000_000)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = archive_batch(
        args.matrix, start=args.start, count=args.count, max_bytes=args.max_bytes
    )
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
