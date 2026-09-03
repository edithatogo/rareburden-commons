#!/usr/bin/env python3
"""Fail-closed preparation for a future exact-file HF promotion."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path
from typing import Any

REQUIRED_CONDITIONS = {"preserve_exact_bytes", "record_source_revision", "record_sha256"}
REQUIRED_EVIDENCE = {
    "exact_file_rights_manifest",
    "immutable_terms_evidence",
    "owner_disposition",
    "destination_allowlist",
    "atomic_destination_receipt",
}


def load_family(path: Path, family_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "bounded_exact_file_candidate_no_promotion":
        raise ValueError("promotion manifest is not a bounded candidate")
    matches = [item for item in payload["families"] if item["id"] == family_id]
    if len(matches) != 1:
        raise ValueError("family must resolve exactly once")
    family = matches[0]
    if not family["prefix"].startswith("releases/") or ".." in family["prefix"]:
        raise ValueError("unsafe family prefix")
    if family["expected_files"] < 1 or family["expected_bytes"] < 1:
        raise ValueError("invalid family bounds")
    if not REQUIRED_CONDITIONS.issubset(family["conditions"]):
        raise ValueError("family is missing mandatory preservation controls")
    return payload, family


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def promote(manifest: Path, family_id: str, *, max_bytes: int) -> dict[str, Any]:
    payload, family = load_family(manifest, family_id)
    if payload.get("promotion_enabled") is not True:
        raise RuntimeError(
            "raw promotion is quarantined; require an exact-file rights manifest, "
            "owner disposition and atomic destination receipt"
        )
    evidence = payload.get("promotion_evidence")
    if not isinstance(evidence, dict) or any(
        evidence.get(key) is not True for key in REQUIRED_EVIDENCE
    ):
        raise RuntimeError(
            "promotion evidence contract is incomplete; remote promotion remains quarantined"
        )
    from huggingface_hub import HfApi, hf_hub_download  # type: ignore[import-not-found]

    if max_bytes < family["expected_bytes"] or max_bytes > 2_000_000_000:
        raise ValueError("family exceeds bounded byte policy")
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required")
    api = HfApi(token=token)
    source = payload["source_repository"]
    revision = payload["source_revision"]
    destination = payload["destination_repository"]
    source_info = api.dataset_info(source, revision=revision, files_metadata=True)
    destination_info = api.dataset_info(destination, files_metadata=True)
    if not source_info.private or destination_info.private:
        raise RuntimeError("promotion visibility boundary is invalid")
    selected = sorted(
        (item for item in source_info.siblings if item.rfilename.startswith(family["prefix"])),
        key=lambda item: item.rfilename,
    )
    if len(selected) != family["expected_files"]:
        raise RuntimeError("source family file count drifted")
    if sum(item.size or 0 for item in selected) != family["expected_bytes"]:
        raise RuntimeError("source family byte count drifted")
    remote = {item.rfilename: item.size for item in destination_info.siblings}
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="rareburden-public-promotion-") as temporary:
        root = Path(temporary)
        for item in selected:
            local = Path(
                hf_hub_download(
                    source,
                    item.rfilename,
                    repo_type="dataset",
                    revision=revision,
                    token=token,
                    local_dir=root,
                )
            )
            size = local.stat().st_size
            digest = sha256_file(local)
            if size != item.size:
                raise RuntimeError(f"source size mismatch: {item.rfilename}")
            status = "already_present"
            if item.rfilename not in remote:
                api.upload_file(
                    path_or_fileobj=str(local),
                    path_in_repo=item.rfilename,
                    repo_id=destination,
                    repo_type="dataset",
                    commit_message=f"Promote rights-cleared {family_id}: {item.rfilename}",
                )
                status = "uploaded"
            elif remote[item.rfilename] != size:
                raise RuntimeError(f"public path conflicts with source size: {item.rfilename}")
            public_local = Path(
                hf_hub_download(
                    destination,
                    item.rfilename,
                    repo_type="dataset",
                    token=token,
                    force_download=True,
                    local_dir=root / "public-check",
                )
            )
            if sha256_file(public_local) != digest:
                raise RuntimeError(f"public hash verification failed: {item.rfilename}")
            results.append(
                {"path": item.rfilename, "bytes": size, "sha256": digest, "status": status}
            )
    receipt = {
        "schema_version": "1.0",
        "status": "remote_hash_verified_public_promotion",
        "family": family_id,
        "licence": family["licence"],
        "licence_url": family["licence_url"],
        "conditions": family["conditions"],
        "source_repository": source,
        "source_revision": revision,
        "destination_repository": destination,
        "files": results,
        "total_bytes": sum(item["bytes"] for item in results),
        "private_source_deleted": False,
        "private_quota_reclaimed": False,
    }
    receipt_path = f"rights-receipts/{family_id}-{revision[:12]}.json"
    api.upload_file(
        path_or_fileobj=io.BytesIO((json.dumps(receipt, sort_keys=True) + "\n").encode()),
        path_in_repo=receipt_path,
        repo_id=destination,
        repo_type="dataset",
        commit_message=f"Record verified public promotion receipt for {family_id}",
    )
    receipt["remote_receipt_path"] = receipt_path
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--max-bytes", type=int, default=2_000_000_000)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    args.receipt.write_text(
        json.dumps(promote(args.manifest, args.family, max_bytes=args.max_bytes), indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
