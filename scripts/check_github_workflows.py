#!/usr/bin/env python3
"""Static, fail-closed policy checks for GitHub Actions workflows."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_UNTRUSTED_CONTEXT_RE = re.compile(
    r"\$\{\{\s*github\.event\.(?:pull_request\.(?:title|body)|issue\.(?:title|body)|"
    r"comment\.body|discussion\.(?:title|body)|review\.body|head_commit\.message)"
)
_DANGEROUS_TRIGGERS = {"pull_request_target", "workflow_run"}


def _load(path: Path) -> dict[str, Any]:
    # BaseLoader preserves the literal key ``on`` rather than applying YAML 1.1 booleans.
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(value, dict):
        raise ValueError("workflow root must be a mapping")
    return value


def _triggers(document: dict[str, Any]) -> set[str]:
    value = document.get("on")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {str(item) for item in value}
    if isinstance(value, dict):
        return {str(item) for item in value}
    return set()


def _permission_errors(value: Any, *, location: str) -> list[str]:
    errors: list[str] = []
    if value is None:
        errors.append(f"{location}: explicit permissions are required")
    elif isinstance(value, str):
        if value in {"write-all", "read-all"}:
            errors.append(f"{location}: {value} is forbidden; declare least-privilege scopes")
        else:
            errors.append(f"{location}: permissions must be a mapping")
    elif not isinstance(value, dict):
        errors.append(f"{location}: permissions must be a mapping")
    else:
        for scope, access in value.items():
            if str(access) not in {"none", "read", "write"}:
                errors.append(f"{location}.{scope}: invalid permission {access!r}")
    return errors


def validate_workflow(path: Path) -> list[str]:
    """Return policy failures for one workflow file."""
    errors: list[str] = []
    try:
        path.read_text(encoding="utf-8")
        document = _load(path)
    except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError) as exc:
        return [f"{path}: cannot parse workflow: {exc}"]

    triggers = _triggers(document)
    for trigger in sorted(triggers & _DANGEROUS_TRIGGERS):
        errors.append(f"{path}: dangerous trigger is forbidden: {trigger}")

    errors.extend(_permission_errors(document.get("permissions"), location=f"{path}:permissions"))
    jobs = document.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        errors.append(f"{path}: jobs must be a non-empty mapping")
        return errors

    for job_name, job in jobs.items():
        location = f"{path}:jobs.{job_name}"
        if not isinstance(job, dict):
            errors.append(f"{location}: job must be a mapping")
            continue
        if "timeout-minutes" not in job:
            errors.append(f"{location}: timeout-minutes is required")
        if str(job.get("continue-on-error", "false")).lower() == "true":
            errors.append(f"{location}: continue-on-error is forbidden for blocking jobs")
        if "permissions" in job:
            errors.extend(
                _permission_errors(job.get("permissions"), location=f"{location}.permissions")
            )
        steps = job.get("steps", [])
        if not isinstance(steps, list):
            errors.append(f"{location}: steps must be a list")
            continue
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"{location}.steps[{index}]: step must be a mapping")
                continue
            uses = step.get("uses")
            if (
                isinstance(uses, str)
                and not uses.startswith("./")
                and not uses.startswith("docker://")
            ):
                if "@" not in uses or not _SHA_RE.fullmatch(uses.rsplit("@", 1)[1]):
                    errors.append(
                        f"{location}.steps[{index}]: third-party actions must use "
                        "a full 40-character commit SHA"
                    )
                if uses.startswith("actions/checkout@"):
                    with_value = step.get("with")
                    persist = (
                        with_value.get("persist-credentials")
                        if isinstance(with_value, dict)
                        else None
                    )
                    if str(persist).lower() != "false":
                        errors.append(
                            f"{location}.steps[{index}]: actions/checkout must set "
                            "persist-credentials: false"
                        )
            run = step.get("run")
            if isinstance(run, str):
                if _UNTRUSTED_CONTEXT_RE.search(run):
                    errors.append(
                        f"{location}.steps[{index}]: untrusted GitHub context is interpolated "
                        "directly into a shell command"
                    )
                if re.search(r"(?:curl|wget)[^\n|]*\|\s*(?:ba)?sh\b", run):
                    errors.append(
                        f"{location}.steps[{index}]: unverified remote script piped to shell"
                    )
    return errors


def validate_workflows(paths: list[Path]) -> list[str]:
    """Return sorted unique failures for workflow files."""
    failures: list[str] = []
    for path in sorted(paths):
        failures.extend(validate_workflow(path))
    return sorted(set(failures))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    paths = args.paths or sorted(Path(".github/workflows").glob("*.y*ml"))
    failures = validate_workflows(paths)
    if failures:
        print("GitHub workflow policy failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"GitHub workflow policy passed for {len(paths)} workflow(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
