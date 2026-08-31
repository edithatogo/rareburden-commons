#!/usr/bin/env python3
"""Verify a clean RareBurden installation using only a staged local wheelhouse."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

# Frozen output for the existing single-row synthetic installed-node check,
# recorded in docs/federated-node-004-offline-install-rehearsal.md.
EXPECTED_OUTPUT_FINGERPRINT = (
    "sha256:32900dea79c7e5dc1fc60db255ac55106ca17a6b5d831e38c7201a1c08080e64"
)


class OfflineInstallError(RuntimeError):
    """Raised when an offline installation or installed-node check fails."""


Runner = Callable[[list[str], Path | None, dict[str, str]], subprocess.CompletedProcess[str]]


def _run(
    arguments: list[str], cwd: Path | None, environment: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            arguments,
            cwd=cwd,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = ""
        if isinstance(exc, subprocess.CalledProcessError):
            detail = (exc.stderr or exc.stdout or "").strip()
        raise OfflineInstallError(
            f"offline command failed: {' '.join(arguments)}" + (f"\n{detail}" if detail else "")
        ) from exc


def _safe_wheel(path: Path, *, label: str) -> Path:
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise OfflineInstallError(f"{label} is not a safe local wheel: {path}")
    resolved = expanded.resolve()
    if not resolved.is_file() or resolved.suffix != ".whl":
        raise OfflineInstallError(f"{label} is not a safe local wheel: {path}")
    return resolved


def check_offline_install(
    *,
    node_wheel: Path,
    wheelhouse: Path,
    python_version: str,
    uv: str = "uv",
    runner: Runner = _run,
) -> dict[str, Any]:
    """Install into a clean environment with network-disabled package commands."""
    node = _safe_wheel(node_wheel, label="node wheel")
    expanded_house = wheelhouse.expanduser()
    if expanded_house.is_symlink():
        raise OfflineInstallError(f"wheelhouse is not a safe directory: {wheelhouse}")
    house = expanded_house.resolve()
    if not house.is_dir():
        raise OfflineInstallError(f"wheelhouse is not a safe directory: {wheelhouse}")
    dependencies = sorted(
        (_safe_wheel(path, label="dependency wheel") for path in house.iterdir()),
        key=lambda path: path.name,
    )
    if not dependencies:
        raise OfflineInstallError("wheelhouse contains no dependency wheels")
    if node in dependencies:
        raise OfflineInstallError("node wheel must not also appear as a dependency wheel")
    artifacts = [node, *dependencies]
    if len({path.name for path in artifacts}) != len(artifacts):
        raise OfflineInstallError("node and dependency wheel filenames must be distinct")
    artifact_sha256 = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in artifacts
    }

    environment = dict(os.environ)
    for variable in (
        "PIP_INDEX_URL",
        "PIP_EXTRA_INDEX_URL",
        "UV_INDEX",
        "UV_DEFAULT_INDEX",
        "UV_EXTRA_INDEX_URL",
        "PYTHONPATH",
        "PYTHONHOME",
    ):
        environment.pop(variable, None)
    environment.update(
        {
            "UV_OFFLINE": "1",
            "UV_NO_PROGRESS": "1",
            "PIP_NO_INDEX": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        }
    )
    with tempfile.TemporaryDirectory(prefix="rareburden-offline-install-") as temporary:
        root = Path(temporary)
        environment_path = root / "venv"
        work = root / "unrelated-working-directory"
        work.mkdir()
        runner(
            [uv, "venv", "--offline", "--python", python_version, str(environment_path)],
            None,
            environment,
        )
        python = (
            environment_path / "Scripts/python.exe"
            if os.name == "nt"
            else environment_path / "bin/python"
        )
        runner(
            [
                uv,
                "pip",
                "install",
                "--offline",
                "--python",
                str(python),
                "--no-index",
                "--find-links",
                str(house),
                str(node),
            ],
            None,
            environment,
        )
        runner([uv, "pip", "check", "--python", str(python)], None, environment)
        check = (
            "import json;"
            "from rareburden.node import run_offline_node,verify_output_fingerprint;"
            "r=run_offline_node([{'group':'synthetic','count':5}],"
            "execution_id='offline-install',coordinator_version='0.1.0',"
            "node_version='0.1.0',analysis_id='synthetic-analysis',"
            "policy_id='synthetic-policy');"
            "verify_output_fingerprint(r);"
            "print(json.dumps({'output_fingerprint':"
            "r['manifest']['output_fingerprint'],'rows':len(r['rows'])},sort_keys=True))"
        )
        result = runner([str(python), "-I", "-c", check], work, environment)
        try:
            installed_result = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise OfflineInstallError("installed-node check did not return JSON") from exc
        if (
            not isinstance(installed_result, dict)
            or set(installed_result) != {"output_fingerprint", "rows"}
            or type(installed_result["rows"]) is not int
            or installed_result["rows"] != 1
            or installed_result["output_fingerprint"] != EXPECTED_OUTPUT_FINGERPRINT
        ):
            raise OfflineInstallError("installed-node check returned an invalid result")
    try:
        unchanged = all(
            _safe_wheel(path, label="installed artifact") == path
            and hashlib.sha256(path.read_bytes()).hexdigest() == artifact_sha256[path.name]
            for path in artifacts
        )
    except OSError as exc:
        raise OfflineInstallError("wheel artifacts changed during offline installation") from exc
    if not unchanged:
        raise OfflineInstallError("wheel artifacts changed during offline installation")
    return {
        "schema_version": "0.1.0",
        "python_version": python_version,
        "network_disabled": True,
        "node_wheel": node.name,
        "dependency_wheel_count": len(dependencies),
        "artifact_sha256": artifact_sha256,
        "installed_result": installed_result,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node-wheel", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--python-version", default="3.13")
    parser.add_argument("--uv", default="uv")
    args = parser.parse_args(argv)
    try:
        receipt = check_offline_install(
            node_wheel=args.node_wheel,
            wheelhouse=args.wheelhouse,
            python_version=args.python_version,
            uv=args.uv,
        )
    except OfflineInstallError as exc:
        parser.error(str(exc))
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
