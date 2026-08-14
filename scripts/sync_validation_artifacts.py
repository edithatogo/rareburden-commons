#!/usr/bin/env python3
"""Bind tracked validation reports to the bounded candidate evidence records."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from collections.abc import Iterable


REPORTS = {
    "coverage.json": ("coverage_json", "application/json"),
    "coverage.xml": ("coverage_xml", "application/xml"),
    "junit.xml": ("junit_xml", "application/xml"),
    "rareburden.cdx.json": ("cyclonedx_sbom", "application/vnd.cyclonedx+json"),
}


class ValidationArtifactError(RuntimeError):
    """Raised when tracked validation evidence is incomplete or inconsistent."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationArtifactError(f"{path} is not a YAML mapping")
    return value


def _git_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    commit = result.stdout.strip()
    if len(commit) != 40:
        raise ValidationArtifactError("cannot resolve an exact 40-character Git commit")
    return commit


def observations(root: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for relative, (kind, media_type) in REPORTS.items():
        path = root / relative
        if not path.is_file():
            raise ValidationArtifactError(f"required validation report is missing: {relative}")
        records[relative] = {
            "path": relative,
            "sha256": _sha256(path),
            "size_bytes": path.stat().st_size,
            "kind": kind,
            "media_type": media_type,
        }
    return records


def sync(root: Path, *, commit: str | None = None) -> None:
    commit = commit or _git_commit(root)
    records = observations(root)
    report_path = root / "docs/validation-report-artifacts-2026-08-03.yml"
    report = _load(report_path)
    report["source_commit"] = commit
    for item in report["artifacts"]:
        record = records[item["path"]]
        item["sha256"] = record["sha256"]
        item["size_bytes"] = record["size_bytes"]
    report_path.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")

    manifest_path = root / "docs/release-manifest-candidate-2026-08-03.yml"
    manifest = _load(manifest_path)
    manifest["repository"]["commit"] = commit
    manifest["repository"]["tree_state"] = "clean"
    for item in manifest["artefacts"]:
        record = records[item["path"]]
        item["sha256"] = record["sha256"]
        item["size_bytes"] = record["size_bytes"]
    manifest["summary"]["artefact_count"] = len(records)
    manifest["summary"]["artefact_bytes"] = sum(record["size_bytes"] for record in records.values())
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    reconciliation_path = root / "docs/release-candidate-evidence-reconciliation-2026-08-04.yml"
    reconciliation = _load(reconciliation_path)
    for item in reconciliation["artifacts"]:
        record = records[item["path"]]
        item["sha256"] = record["sha256"]
        item["size_bytes"] = record["size_bytes"]
    reconciliation_path.write_text(
        yaml.safe_dump(reconciliation, sort_keys=False), encoding="utf-8"
    )


def check(root: Path) -> None:
    records = observations(root)
    manifest = _load(root / "docs/release-manifest-candidate-2026-08-03.yml")
    report = _load(root / "docs/validation-report-artifacts-2026-08-03.yml")
    reconciliation = _load(root / "docs/release-candidate-evidence-reconciliation-2026-08-04.yml")
    commit = manifest["repository"]["commit"]
    if not isinstance(commit, str) or len(commit) != 40:
        raise ValidationArtifactError("candidate manifest is not bound to an exact commit")
    if report["source_commit"] != commit:
        raise ValidationArtifactError("validation report and candidate commit bindings differ")
    documents: Iterable[tuple[dict[str, Any], str]] = (
        (manifest, "artefacts"),
        (report, "artifacts"),
        (reconciliation, "artifacts"),
    )
    for document, key in documents:
        indexed = {item["path"]: item for item in document[key]}
        if set(indexed) != set(records):
            raise ValidationArtifactError(f"{key} does not enumerate the required reports")
        for path, record in records.items():
            item = indexed[path]
            if item["sha256"] != record["sha256"] or item["size_bytes"] != record["size_bytes"]:
                raise ValidationArtifactError(f"validation evidence drift detected: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path())
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--commit")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.write:
        sync(root, commit=args.commit)
    check(root)
    print("Validation report provenance is complete and internally consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
