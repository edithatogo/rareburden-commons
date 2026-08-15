#!/usr/bin/env python3
"""Advance a private UTS historical archive from remote receipt checkpoints."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from scripts.archive_uts_batch import _load_family, archive_uts_batch

_RECEIPT = re.compile(r"^(\d{5})-(\d{5})\.json$")


def _artifact_path(release_type: str, release: dict[str, Any]) -> str:
    return "/".join(
        (
            "licensed-private",
            "uts",
            release_type,
            str(release["releaseVersion"]),
            str(release["fileName"]),
        )
    )


def _receipt_ranges(remote_files: set[str], release_type: str) -> list[tuple[int, int]]:
    prefix = f"manifests/uts/receipts/{release_type}/"
    ranges: list[tuple[int, int]] = []
    for path in remote_files:
        if not path.startswith(prefix):
            continue
        match = _RECEIPT.fullmatch(path.removeprefix(prefix))
        if not match:
            continue
        start, end = (int(value) for value in match.groups())
        if start > end:
            raise ValueError(f"invalid remote receipt range: {path}")
        ranges.append((start, end))
    return sorted(ranges)


def _covered(index: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= index <= end for start, end in ranges)


def plan_frontier(
    manifest: Path,
    family_order: list[str],
    remote_files: set[str],
    *,
    minimum_index: int,
    only_family: str | None = None,
) -> list[dict[str, object]]:
    """Return every historical item with a verified or pending checkpoint state."""
    if minimum_index < 1:
        raise ValueError("historical frontier must not include current index zero")
    selected_families = family_order
    if only_family and only_family != "auto":
        if only_family not in family_order:
            raise ValueError(f"family is absent from frontier plan: {only_family}")
        selected_families = [only_family]

    plan: list[dict[str, object]] = []
    for release_type in selected_families:
        releases = _load_family(manifest, release_type)
        ranges = _receipt_ranges(remote_files, release_type)
        for index, release in enumerate(releases[minimum_index:], start=minimum_index):
            artifact = _artifact_path(release_type, release)
            has_artifact = artifact in remote_files
            has_receipt = _covered(index, ranges)
            if has_artifact != has_receipt:
                raise RuntimeError(
                    f"remote checkpoint is inconsistent for {release_type} index {index}: "
                    f"artifact={has_artifact} receipt={has_receipt}"
                )
            plan.append(
                {
                    "release_type": release_type,
                    "index": index,
                    "release_version": release["releaseVersion"],
                    "file_name": release["fileName"],
                    "artifact_path": artifact,
                    "status": "verified" if has_artifact else "pending",
                }
            )
    return plan


def family_cursors(plan: list[dict[str, object]], family_order: list[str]) -> dict[str, object]:
    """Summarise the first pending index and verified/pending counts per family."""
    result: dict[str, object] = {}
    for release_type in family_order:
        family = [item for item in plan if item["release_type"] == release_type]
        pending = [item for item in family if item["status"] == "pending"]
        result[release_type] = {
            "next_index": pending[0]["index"] if pending else None,
            "verified_historical": sum(item["status"] == "verified" for item in family),
            "pending_historical": len(pending),
        }
    return result


def archive_frontier(
    manifest: Path,
    frontier: Path,
    *,
    only_family: str,
    max_artifacts: int,
    max_bytes: int,
    max_minutes: int,
) -> dict[str, object]:
    """Advance a bounded number of items, refreshing remote state after each upload."""
    from huggingface_hub import HfApi  # type: ignore[import-not-found]

    token = os.environ.get("HF_TOKEN")
    if not token or not os.environ.get("UMLS_API_KEY"):
        raise RuntimeError("HF_TOKEN and UMLS_API_KEY are required")
    document = json.loads(frontier.read_text(encoding="utf-8"))
    family_order = document["family_order"]
    limits = document["run_limits"]
    if not isinstance(family_order, list) or not all(isinstance(x, str) for x in family_order):
        raise ValueError("frontier family_order must be an array of strings")
    if not 1 <= max_artifacts <= int(limits["maximum_max_artifacts"]):
        raise ValueError("max_artifacts exceeds the frontier policy")
    if not 1 <= max_bytes <= int(limits["maximum_max_bytes"]):
        raise ValueError("max_bytes exceeds the frontier policy")
    if not 1 <= max_minutes <= int(limits["maximum_max_minutes"]):
        raise ValueError("max_minutes exceeds the frontier policy")

    repo_id = str(document["destination"])
    api = HfApi(token=token)
    info = api.dataset_info(repo_id, files_metadata=True)
    if not info.private:
        raise RuntimeError("UTS destination must remain private")
    remote_files = {entry.rfilename for entry in info.siblings}
    plan = plan_frontier(
        manifest,
        family_order,
        remote_files,
        minimum_index=int(document["minimum_historical_index"]),
        only_family=only_family,
    )
    cursor_families = family_order if only_family == "auto" else [only_family]
    initial_cursors = family_cursors(plan, cursor_families)
    pending = [item for item in plan if item["status"] == "pending"]
    results: list[dict[str, object]] = []
    used_bytes = 0
    started = time.monotonic()
    stop_reason = "frontier_exhausted"
    for item in pending:
        if len(results) >= max_artifacts:
            stop_reason = "artifact_budget_reached"
            break
        if results and time.monotonic() - started >= max_minutes * 60:
            stop_reason = "time_budget_reached"
            break
        remaining = max_bytes - used_bytes
        if remaining <= 0:
            stop_reason = "byte_budget_reached"
            break
        index = item["index"]
        if not isinstance(index, int):  # defensive guard for the internal plan contract
            raise RuntimeError("frontier index is not an integer")
        receipt = archive_uts_batch(
            manifest,
            str(item["release_type"]),
            repo_id,
            start=index,
            count=1,
            max_bytes=remaining,
        )
        used_bytes += int(receipt["bytes"])
        results.append(
            {
                **item,
                "status": "archived",
                "bytes": receipt["bytes"],
                "sha256": receipt["artifacts"][0]["sha256"],
                "commit": receipt["commit"],
            }
        )
        remote_files.add(str(item["artifact_path"]))
        receipt_path = f"manifests/uts/receipts/{item['release_type']}/{index:05d}-{index:05d}.json"
        remote_files.add(receipt_path)
    else:
        stop_reason = "frontier_exhausted"

    final_plan = plan_frontier(
        manifest,
        family_order,
        remote_files,
        minimum_index=int(document["minimum_historical_index"]),
        only_family=only_family,
    )
    return {
        "schema_version": "1.0",
        "status": "private_historical_frontier_checkpoint",
        "repository": repo_id,
        "selected_family": only_family,
        "limits": {
            "max_artifacts": max_artifacts,
            "max_bytes": max_bytes,
            "max_minutes": max_minutes,
        },
        "used_bytes": used_bytes,
        "archived_count": len(results),
        "stop_reason": stop_reason,
        "initial_cursors": initial_cursors,
        "final_cursors": family_cursors(final_plan, cursor_families),
        "results": results,
        "claims": {
            "public_redistribution": False,
            "selected_family_complete": not any(item["status"] == "pending" for item in final_plan),
            "historical_completeness": only_family == "auto"
            and not any(item["status"] == "pending" for item in final_plan),
            "native_edition_completeness": False,
            "production_activation": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("frontier", type=Path)
    parser.add_argument("--family", default="auto")
    parser.add_argument("--max-artifacts", type=int, default=3)
    parser.add_argument("--max-bytes", type=int, default=8_000_000_000)
    parser.add_argument("--max-minutes", type=int, default=180)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = archive_frontier(
        args.manifest,
        args.frontier,
        only_family=args.family,
        max_artifacts=args.max_artifacts,
        max_bytes=args.max_bytes,
        max_minutes=args.max_minutes,
    )
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
