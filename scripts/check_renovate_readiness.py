#!/usr/bin/env python3
"""Validate repository-owned Renovate prerequisites without inferring app execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class RenovateReadinessError(ValueError):
    """Raised when the repository-side Renovate contract drifts."""


def validate_renovate_readiness(root: Path) -> dict[str, Any]:
    config_path = root / "renovate.json"
    if not config_path.is_file():
        raise RenovateReadinessError("renovate.json is required")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    extends = config.get("extends")
    if not isinstance(extends, list) or "github>edithatogo/renovate-config" not in extends:
        raise RenovateReadinessError("shared Renovate preset must remain inherited")
    if config.get("dependencyDashboard") is not True:
        raise RenovateReadinessError("Renovate Dependency Dashboard must remain enabled")
    if config.get("prConcurrentLimit") != 5 or config.get("prHourlyLimit") != 2:
        raise RenovateReadinessError("bounded Renovate pull-request limits changed")
    if not config.get("schedule"):
        raise RenovateReadinessError("Renovate schedule must remain explicit")
    ignored_paths = config.get("ignorePaths")
    required_ignored_paths = {"requirements.txt", "requirements-dev.txt"}
    if not isinstance(ignored_paths, list) or not required_ignored_paths.issubset(
        set(ignored_paths)
    ):
        raise RenovateReadinessError(
            "generated requirements exports must be ignored by Renovate"
        )
    if (root / ".github" / "dependabot.yml").exists() or (
        root / ".github" / "dependabot.yaml"
    ).exists():
        raise RenovateReadinessError("Dependabot must not compete with Renovate")
    return {
        "schema_version": "1.0",
        "status": "repository_configuration_ready",
        "dependency_dashboard_configured": True,
        "generated_requirements_exports_ignored": True,
        "hosted_app_execution_observed": False,
        "hosted_evidence_required": "Renovate-authored Dependency Dashboard or pull request",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path())
    args = parser.parse_args()
    print(json.dumps(validate_renovate_readiness(args.root.resolve()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
