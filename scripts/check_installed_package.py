#!/usr/bin/env python3
"""Exercise an installed wheel from outside the source checkout."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


class InstalledPackageCheckError(RuntimeError):
    """Raised when an isolated installed-package check fails."""


def _run(arguments: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            arguments,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        if isinstance(exc, subprocess.CalledProcessError):
            detail = (exc.stderr or exc.stdout or "").strip()
        else:
            detail = str(exc)
        raise InstalledPackageCheckError(
            f"Command failed: {' '.join(arguments)}" + (f"\n{detail}" if detail else "")
        ) from exc


def _venv_python(environment: Path) -> Path:
    relative = Path("Scripts/python.exe") if os.name == "nt" else Path("bin/python")
    return environment / relative


def check_installed_wheel(wheel: Path, *, uv: str, python_version: str) -> None:
    """Install *wheel* into an empty environment and run the packaged reference workflow."""
    wheel = wheel.expanduser().resolve()
    if wheel.is_symlink() or not wheel.is_file():
        raise InstalledPackageCheckError(f"Wheel is missing or unsafe: {wheel}")

    with tempfile.TemporaryDirectory(prefix="rareburden-installed-") as temporary:
        root = Path(temporary)
        environment = root / "venv"
        work = root / "unrelated-working-directory"
        work.mkdir()
        _run([uv, "venv", "--python", python_version, str(environment)])
        python = _venv_python(environment)
        _run([uv, "pip", "install", "--python", str(python), str(wheel)])

        doctor = _run(
            [str(python), "-m", "rareburden", "doctor", "--json"],
            cwd=work,
        )
        doctor_payload = json.loads(doctor.stdout)
        if doctor_payload.get("ok") is not True:
            raise InstalledPackageCheckError("Installed-package doctor did not report success")
        repository_root = Path(str(doctor_payload.get("root", ""))).resolve()
        if work == repository_root or work in repository_root.parents:
            raise InstalledPackageCheckError(
                "Installed package resolved the caller directory instead of packaged resources"
            )

        output = Path("outputs/reference")
        _run(
            [
                str(python),
                "-m",
                "rareburden",
                "demo-public-foundation",
                "--output",
                output.as_posix(),
                "--created-at",
                "2026-07-27T00:00:00Z",
                "--json",
            ],
            cwd=work,
        )
        release = work / output
        if not release.is_dir():
            raise InstalledPackageCheckError(
                "Installed-package relative output was not written beneath the caller directory"
            )

        verification = _run(
            [
                str(python),
                "-m",
                "rareburden",
                "verify-reference-release",
                "--release",
                output.as_posix(),
                "--verified-at",
                "2026-07-27T01:00:00Z",
                "--json",
            ],
            cwd=work,
        )
        payload = json.loads(verification.stdout)
        if payload.get("status") != "passed":
            raise InstalledPackageCheckError("Installed reference release did not verify")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--uv", default="uv")
    parser.add_argument("--python-version", default="3.13")
    args = parser.parse_args()
    try:
        check_installed_wheel(
            args.wheel,
            uv=str(args.uv),
            python_version=str(args.python_version),
        )
    except (InstalledPackageCheckError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Installed-package reference workflow passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
