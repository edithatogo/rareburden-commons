from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.build_sbom import SbomError, build_sbom, write_sbom


def test_sbom_is_deterministic_and_tracks_locked_dependencies(tmp_path: Path) -> None:
    lock = tmp_path / "uv.lock"
    lock.write_text(
        """version = 1
revision = 3
requires-python = ">=3.11"

[[package]]
name = "Example_App"
version = "1.0.0"
dependencies = [{ name = "Dependency" }]

[[package]]
name = "dependency"
version = "2.0.0"
""",
        encoding="utf-8",
    )
    first = build_sbom(lock)
    second = build_sbom(lock)
    assert first == second
    assert first["bomFormat"] == "CycloneDX"
    assert first["specVersion"] == "1.5"
    assert [component["name"] for component in first["components"]] == [
        "dependency",
        "example-app",
    ]
    app_ref = next(
        component["bom-ref"]
        for component in first["components"]
        if component["name"] == "example-app"
    )
    dependency_ref = next(
        component["bom-ref"]
        for component in first["components"]
        if component["name"] == "dependency"
    )
    relation = next(item for item in first["dependencies"] if item["ref"] == app_ref)
    assert relation["dependsOn"] == [dependency_ref]
    output = tmp_path / "sbom.json"
    write_sbom(lock, output)
    assert json.loads(output.read_text(encoding="utf-8")) == first


@pytest.mark.parametrize(
    "content",
    [
        "not toml = [",
        "version = 1\n",
        '[[package]]\nname = "missing-version"\n',
        '[[package]]\nname = "a"\nversion = "1"\ndependencies = "bad"\n',
    ],
)
def test_sbom_rejects_invalid_lock_documents(tmp_path: Path, content: str) -> None:
    lock = tmp_path / "uv.lock"
    lock.write_text(content, encoding="utf-8")
    with pytest.raises(SbomError):
        build_sbom(lock)
