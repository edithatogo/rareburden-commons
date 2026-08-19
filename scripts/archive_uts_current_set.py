#!/usr/bin/env python3
"""Archive the newest release from every checked-in UTS family sequentially."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from scripts.archive_uts_batch import _load_family, archive_uts_batch

_REPO_ID = "edithatogo/hpo-licensed-ontology-archive"


def _remote_paths(release_type: str, release: dict[str, Any]) -> tuple[str, str]:
    artifact = "/".join(
        (
            "licensed-private",
            "uts",
            release_type,
            str(release["releaseVersion"]),
            str(release["fileName"]),
        )
    )
    receipt = f"manifests/uts/receipts/{release_type}/00000-00000.json"
    return artifact, receipt


def plan_current_set(manifest: Path, remote_files: set[str]) -> list[dict[str, object]]:
    document = json.loads(manifest.read_text(encoding="utf-8"))
    families = document.get("families", [])
    plan: list[dict[str, object]] = []
    for family in families:
        release_type = str(family["release_type"])
        release = _load_family(manifest, release_type)[0]
        artifact, receipt = _remote_paths(release_type, release)
        plan.append(
            {
                "release_type": release_type,
                "release_version": release["releaseVersion"],
                "artifact_path": artifact,
                "receipt_path": receipt,
                "already_archived": artifact in remote_files and receipt in remote_files,
            }
        )
    return plan


def archive_current_set(manifest: Path, *, max_bytes_per_family: int) -> dict[str, object]:
    from huggingface_hub import HfApi  # type: ignore[import-not-found]

    token = os.environ.get("HF_TOKEN")
    if not token or not os.environ.get("UMLS_API_KEY"):
        raise RuntimeError("HF_TOKEN and UMLS_API_KEY are required")
    api = HfApi(token=token)
    info = api.dataset_info(_REPO_ID, files_metadata=True)
    if not info.private:
        raise RuntimeError("UTS destination must remain private")
    remote_files = {entry.rfilename for entry in info.siblings}
    plan = plan_current_set(manifest, remote_files)
    results: list[dict[str, object]] = []
    for item in plan:
        if item["already_archived"]:
            results.append({**item, "status": "already_receipt_verified"})
            continue
        if results:
            time.sleep(2.0)
        receipt = archive_uts_batch(
            manifest,
            str(item["release_type"]),
            _REPO_ID,
            start=0,
            count=1,
            max_bytes=max_bytes_per_family,
        )
        results.append({**item, "status": "archived", "commit": receipt["commit"]})
    return {
        "schema_version": "1.0",
        "status": "private_current_release_set",
        "repository": _REPO_ID,
        "family_count": len(plan),
        "results": results,
        "claims": {"public_redistribution": False, "native_edition_completeness": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--max-bytes-per-family", type=int, default=8_000_000_000)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = archive_current_set(args.manifest, max_bytes_per_family=args.max_bytes_per_family)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
