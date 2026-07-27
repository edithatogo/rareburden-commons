"""Machine-auditable lineage closure for transformation outputs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from rareburden.provenance import content_id, sha256_file


class LineageAuditError(ValueError):
    """Raised when lineage inputs are malformed or ambiguous."""


def _output_index(
    transformation_runs: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    producers: dict[str, Mapping[str, Any]] = {}
    failures: list[str] = []
    seen_runs: set[str] = set()
    for run in transformation_runs:
        run_id = run.get("transformation_run_id")
        if not isinstance(run_id, str):
            failures.append("transformation run is missing an identifier")
            continue
        if run_id in seen_runs:
            failures.append(f"duplicate transformation run identifier: {run_id}")
        seen_runs.add(run_id)
        outputs = run.get("outputs")
        if not isinstance(outputs, list):
            failures.append(f"transformation run {run_id} has invalid outputs")
            continue
        for output in outputs:
            if not isinstance(output, Mapping) or not isinstance(output.get("path"), str):
                failures.append(f"transformation run {run_id} has invalid output artefact")
                continue
            path = str(output["path"])
            if path in producers:
                other = producers[path].get("transformation_run_id")
                failures.append(f"multiple producers for {path}: {other}, {run_id}")
                continue
            producers[path] = run
    return producers, failures


def build_lineage_audit(
    *,
    root: Path,
    release_id: str,
    transformation_runs: Sequence[Mapping[str, Any]],
    expected_outputs: Sequence[str],
    created_at: str,
    exempt_outputs: Sequence[str] = (),
) -> dict[str, Any]:
    """Audit that every expected scientific output has one verified producer.

    Metadata that is necessarily created after transformation closure (for example the
    lineage audit itself, RO-Crate metadata and the release manifest) can be named in
    ``exempt_outputs``.  Exemptions are explicit and included in the audit identity.
    """
    resolved_root = root.expanduser().resolve()
    producers, failures = _output_index(transformation_runs)
    expected = sorted(set(expected_outputs))
    exempt = sorted(set(exempt_outputs))
    if set(expected) & set(exempt):
        raise LineageAuditError("An expected output cannot also be lineage-exempt")

    checks: list[dict[str, Any]] = []
    for path_text in expected:
        path = Path(path_text)
        if path.is_absolute() or ".." in path.parts or "\\" in path_text:
            failures.append(f"unsafe expected output path: {path_text}")
            continue
        producer = producers.get(path_text)
        if producer is None:
            failures.append(f"untraced expected output: {path_text}")
            continue
        matching = [
            item
            for item in producer["outputs"]
            if isinstance(item, Mapping) and item.get("path") == path_text
        ]
        if len(matching) != 1:
            failures.append(f"ambiguous producer record for {path_text}")
            continue
        file_path = resolved_root / path
        if file_path.is_symlink() or not file_path.is_file():
            failures.append(f"expected output is missing or unsafe: {path_text}")
            continue
        try:
            file_path.resolve().relative_to(resolved_root)
        except ValueError:
            failures.append(f"expected output escapes audit root: {path_text}")
            continue
        digest, size = sha256_file(file_path)
        record = matching[0]
        if digest != record.get("sha256"):
            failures.append(f"producer checksum mismatch: {path_text}")
            continue
        if size != record.get("size_bytes"):
            failures.append(f"producer size mismatch: {path_text}")
            continue
        checks.append(
            {
                "path": path_text,
                "status": "passed",
                "producer": str(producer["transformation_run_id"]),
                "sha256": digest,
            }
        )

    for run in transformation_runs:
        run_id = str(run.get("transformation_run_id", "unknown"))
        inputs = run.get("inputs")
        if not isinstance(inputs, list) or not inputs:
            failures.append(f"transformation run {run_id} has no recorded inputs")
            continue
        for item in inputs:
            if not isinstance(item, Mapping):
                failures.append(f"transformation run {run_id} has malformed input")
                continue
            role = item.get("role")
            if role == "source_data" and not (
                item.get("source_release_id") and item.get("acquisition_manifest_id")
            ):
                failures.append(
                    "source-data input lacks acquisition lineage in run "
                    f"{run_id}: {item.get('path')}"
                )

    status = "passed" if not failures else "failed"
    core = {
        "release_id": release_id,
        "created_at": created_at,
        "status": status,
        "transformation_run_ids": sorted(
            str(run.get("transformation_run_id")) for run in transformation_runs
        ),
        "expected_outputs": expected,
        "exempt_outputs": exempt,
        "checks": sorted(checks, key=lambda item: str(item["path"])),
        "failures": sorted(set(failures)),
        "summary": {
            "expected_output_count": len(expected),
            "verified_output_count": len(checks),
            "failure_count": len(set(failures)),
        },
    }
    return {
        "schema_version": "1.0.0",
        "lineage_audit_id": content_id("audit", core),
        **core,
    }


def require_lineage_audit_pass(audit: Mapping[str, Any]) -> None:
    """Raise when a lineage audit does not pass without failures."""
    failures = audit.get("failures")
    if audit.get("status") != "passed" or not isinstance(failures, list) or failures:
        details = "; ".join(str(item) for item in failures or ["unknown lineage failure"])
        raise LineageAuditError(f"Lineage audit failed: {details}")


__all__ = ["LineageAuditError", "build_lineage_audit", "require_lineage_audit_pass"]
