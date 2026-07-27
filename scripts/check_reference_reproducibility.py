#!/usr/bin/env python3
"""Rebuild the synthetic reference twice and prove exact deterministic equivalence."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from rareburden.verification import verify_reference_release


class ReferenceReproducibilityError(RuntimeError):
    """Raised when independent local reference executions do not agree exactly."""


@dataclass(frozen=True)
class ReproducibilitySummary:
    file_count: int
    byte_count: int
    verification_checks: int


def _run_reference(*, root: Path, output: Path, created_at: str, hash_seed: str) -> None:
    environment = os.environ.copy()
    source = str(root / "src")
    environment["PYTHONPATH"] = source + os.pathsep + environment.get("PYTHONPATH", "")
    environment["PYTHONHASHSEED"] = hash_seed
    environment["TZ"] = "UTC"
    command = [
        sys.executable,
        "-m",
        "rareburden",
        "demo-public-foundation",
        "--root",
        str(root),
        "--output",
        str(output),
        "--created-at",
        created_at,
        "--json",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            env=environment,
            text=True,
            capture_output=True,
            check=True,
            timeout=120,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        stderr = getattr(exc, "stderr", "") or ""
        raise ReferenceReproducibilityError(
            f"Reference execution with PYTHONHASHSEED={hash_seed} failed: {stderr.strip() or exc}"
        ) from exc
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ReferenceReproducibilityError("Reference command did not emit valid JSON") from exc
    if not isinstance(payload, dict) or payload.get("generated_file_count", 0) < 1:
        raise ReferenceReproducibilityError("Reference command returned an invalid completion summary")


def _files(root: Path) -> dict[str, bytes]:
    records: dict[str, bytes] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ReferenceReproducibilityError(f"Reference output contains a symlink: {path}")
        if path.is_file():
            records[path.relative_to(root).as_posix()] = path.read_bytes()
    return records


def check_reference_reproducibility(
    root: Path,
    *,
    created_at: str,
    work_directory: Path | None = None,
) -> ReproducibilitySummary:
    """Run the reference twice in separate processes and compare every output byte."""
    repository_root = root.expanduser().resolve()
    if not repository_root.is_dir() or repository_root.is_symlink():
        raise ReferenceReproducibilityError(f"Repository root is missing or unsafe: {root}")

    temporary: tempfile.TemporaryDirectory[str] | None = None
    if work_directory is None:
        temporary = tempfile.TemporaryDirectory(prefix="rareburden-repro-")
        work_root = Path(temporary.name)
    else:
        work_root = work_directory.expanduser().resolve()
        if work_root.exists():
            if work_root.is_symlink() or not work_root.is_dir():
                raise ReferenceReproducibilityError(f"Work directory is unsafe: {work_root}")
            shutil.rmtree(work_root)
        work_root.mkdir(parents=True)

    try:
        first = work_root / "run-a"
        second = work_root / "run-b"
        _run_reference(root=repository_root, output=first, created_at=created_at, hash_seed="11")
        _run_reference(root=repository_root, output=second, created_at=created_at, hash_seed="8675309")

        first_files = _files(first)
        second_files = _files(second)
        if first_files.keys() != second_files.keys():
            missing = sorted(first_files.keys() - second_files.keys())
            extra = sorted(second_files.keys() - first_files.keys())
            raise ReferenceReproducibilityError(f"Reference file sets differ: missing={missing}; extra={extra}")
        changed = sorted(path for path in first_files if first_files[path] != second_files[path])
        if changed:
            raise ReferenceReproducibilityError(
                "Reference outputs are not byte-for-byte deterministic: " + ", ".join(changed)
            )

        checks = 0
        for output in (first, second):
            report = verify_reference_release(
                output,
                schema_root=output / "materials/schemas",
                verified_at=created_at,
            )
            if report.get("status") != "passed":
                failures = [
                    failure
                    for check in report.get("checks", [])
                    if isinstance(check, dict)
                    for failure in check.get("failures", [])
                ]
                raise ReferenceReproducibilityError(
                    "Independent reference verification failed: " + "; ".join(map(str, failures))
                )
            checks += len(report.get("checks", []))
        return ReproducibilitySummary(
            file_count=len(first_files),
            byte_count=sum(len(value) for value in first_files.values()),
            verification_checks=checks,
        )
    finally:
        if temporary is not None:
            temporary.cleanup()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--created-at", default="2026-07-20T00:00:00Z")
    parser.add_argument("--work-directory", type=Path)
    args = parser.parse_args()
    try:
        summary = check_reference_reproducibility(
            args.root,
            created_at=args.created_at,
            work_directory=args.work_directory,
        )
    except ReferenceReproducibilityError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(
        "Reference reproducibility passed: "
        f"{summary.file_count} files, {summary.byte_count} bytes, "
        f"{summary.verification_checks} verification checks across two isolated executions."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
