from __future__ import annotations

import importlib.util
import json
import zipfile
from pathlib import Path
from types import ModuleType

import pytest


def _load_script() -> ModuleType:
    script = Path(__file__).parents[1] / "scripts" / "build_node_bundle.py"
    spec = importlib.util.spec_from_file_location("build_node_bundle", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUNDLE = _load_script()


def _wheel(path: Path, *, member: str = "package/__init__.py", content: bytes = b"") -> Path:
    parts = path.name.removesuffix(".whl").split("-")
    dist_info = f"{parts[0]}-{parts[1]}.dist-info"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(member, content)
        archive.writestr(
            f"{dist_info}/METADATA",
            (f"Metadata-Version: 2.1\nName: {parts[0]}\nVersion: {parts[1]}\n").encode(),
        )
        archive.writestr(f"{dist_info}/WHEEL", b"Wheel-Version: 1.0\n")
        archive.writestr(f"{dist_info}/RECORD", b"")
    return path


def _rewrite_bundle(
    path: Path, replacements: dict[str, bytes], extra: dict[str, bytes] | None = None
) -> None:
    with zipfile.ZipFile(path) as archive:
        entries = {info.filename: archive.read(info) for info in archive.infolist()}
    entries.update(replacements)
    entries.update(extra or {})
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)


def test_build_is_deterministic_and_verifiable(tmp_path: Path) -> None:
    node = _wheel(tmp_path / "rareburden-1.0-py3-none-any.whl", content=b"node")
    dependency = _wheel(tmp_path / "dependency-2.0-py3-none-any.whl", content=b"dependency")
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    manifest = BUNDLE.build_node_bundle(first, node, [dependency])
    BUNDLE.build_node_bundle(second, node, [dependency])

    assert first.read_bytes() == second.read_bytes()
    assert BUNDLE.verify_node_bundle(first) == manifest
    assert [record["filename"] for record in manifest["artifacts"]] == [
        dependency.name,
        node.name,
    ]
    assert {record["role"] for record in manifest["artifacts"]} == {"node", "dependency"}
    with zipfile.ZipFile(first) as archive:
        assert archive.namelist() == [
            "manifest.json",
            f"wheels/{dependency.name}",
            f"wheels/{node.name}",
        ]
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist())


@pytest.mark.parametrize(
    "artifact",
    [
        "missing.whl",
        "https://example.test/package.whl",
    ],
)
def test_build_rejects_missing_and_remote_artifacts(tmp_path: Path, artifact: str) -> None:
    node = _wheel(tmp_path / "rareburden-1.0-py3-none-any.whl")

    with pytest.raises(BUNDLE.NodeBundleError):
        BUNDLE.build_node_bundle(tmp_path / "bundle.zip", node, [artifact])


def test_build_rejects_non_wheel_symlink_and_duplicate_filename(tmp_path: Path) -> None:
    node = _wheel(tmp_path / "rareburden-1.0-py3-none-any.whl")
    not_wheel = tmp_path / "dependency.txt"
    not_wheel.write_bytes(b"not a wheel")
    linked = tmp_path / "linked.whl"
    linked.symlink_to(node)
    duplicate_directory = tmp_path / "duplicate"
    duplicate_directory.mkdir()
    duplicate = _wheel(duplicate_directory / node.name)

    with pytest.raises(BUNDLE.NodeBundleError, match="safely named wheel"):
        BUNDLE.build_node_bundle(tmp_path / "bundle.zip", node, [not_wheel])
    with pytest.raises(BUNDLE.NodeBundleError, match="symbolic link"):
        BUNDLE.build_node_bundle(tmp_path / "bundle.zip", linked)
    with pytest.raises(BUNDLE.NodeBundleError, match="duplicate wheel filename"):
        BUNDLE.build_node_bundle(tmp_path / "bundle.zip", node, [duplicate])


def test_build_rejects_invalid_or_unsafe_wheel_archive(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid-1.0-py3-none-any.whl"
    invalid.write_bytes(b"not zip")
    unsafe = _wheel(tmp_path / "unsafe-1.0-py3-none-any.whl", member="../escape")

    with pytest.raises(BUNDLE.NodeBundleError, match="valid wheel"):
        BUNDLE.build_node_bundle(tmp_path / "bundle.zip", invalid)
    with pytest.raises(BUNDLE.NodeBundleError, match="unsafe member"):
        BUNDLE.build_node_bundle(tmp_path / "bundle.zip", unsafe)


def test_verify_rejects_tampering_and_unmanifested_members(tmp_path: Path) -> None:
    node = _wheel(tmp_path / "rareburden-1.0-py3-none-any.whl", content=b"node")
    bundle = tmp_path / "bundle.zip"
    BUNDLE.build_node_bundle(bundle, node)

    _rewrite_bundle(bundle, {f"wheels/{node.name}": b"changed"})
    with pytest.raises(BUNDLE.NodeBundleError, match="integrity"):
        BUNDLE.verify_node_bundle(bundle)

    BUNDLE.build_node_bundle(bundle, node)
    _rewrite_bundle(bundle, {}, {"unexpected.txt": b"surprise"})
    with pytest.raises(BUNDLE.NodeBundleError, match="unmanifested"):
        BUNDLE.verify_node_bundle(bundle)


def test_verify_rejects_manifest_role_and_canonical_encoding(tmp_path: Path) -> None:
    node = _wheel(tmp_path / "rareburden-1.0-py3-none-any.whl")
    bundle = tmp_path / "bundle.zip"
    manifest = BUNDLE.build_node_bundle(bundle, node)
    manifest["artifacts"][0]["role"] = "dependency"
    _rewrite_bundle(bundle, {"manifest.json": (json.dumps(manifest) + "\n").encode()})

    with pytest.raises(BUNDLE.NodeBundleError, match="exactly one node"):
        BUNDLE.verify_node_bundle(bundle)

    BUNDLE.build_node_bundle(bundle, node)
    with zipfile.ZipFile(bundle) as archive:
        parsed = json.loads(archive.read("manifest.json"))
    _rewrite_bundle(bundle, {"manifest.json": json.dumps(parsed).encode()})
    with pytest.raises(BUNDLE.NodeBundleError, match="canonically encoded"):
        BUNDLE.verify_node_bundle(bundle)


def test_build_refuses_to_overwrite_input(tmp_path: Path) -> None:
    node = _wheel(tmp_path / "rareburden-1.0-py3-none-any.whl")

    with pytest.raises(BUNDLE.NodeBundleError, match="overwrite"):
        BUNDLE.build_node_bundle(node, node)


def test_build_rejects_wheel_without_required_metadata(tmp_path: Path) -> None:
    wheel = tmp_path / "rareburden-1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("rareburden/__init__.py", b"")
    with pytest.raises(BUNDLE.NodeBundleError, match="required metadata"):
        BUNDLE.build_node_bundle(tmp_path / "bundle.zip", wheel)


def test_archive_resource_bounds_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wheel = _wheel(tmp_path / "rareburden-1.0-py3-none-any.whl")
    monkeypatch.setattr(BUNDLE, "MAX_ARCHIVE_MEMBERS", 2)
    with pytest.raises(BUNDLE.NodeBundleError, match="too many"):
        BUNDLE.build_node_bundle(tmp_path / "bundle.zip", wheel)


def test_verify_rejects_self_consistent_non_wheel_payload(tmp_path: Path) -> None:
    wheel_name = "rareburden-1.0-py3-none-any.whl"
    payload = b"not a wheel"
    manifest = {
        "artifacts": [
            {
                "filename": wheel_name,
                "role": "node",
                "sha256": BUNDLE._sha256(payload),
                "size": len(payload),
            }
        ],
        "bundle_format": "rareburden-offline-node-wheel-bundle",
        "schema_version": BUNDLE.SCHEMA_VERSION,
    }
    bundle = tmp_path / "bundle.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("manifest.json", BUNDLE._canonical_json(manifest))
        archive.writestr(f"wheels/{wheel_name}", payload)
    with pytest.raises(BUNDLE.NodeBundleError, match="valid wheel"):
        BUNDLE.verify_node_bundle(bundle)


def test_build_requires_rareburden_as_node_distribution(tmp_path: Path) -> None:
    other = _wheel(tmp_path / "other-1.0-py3-none-any.whl")
    with pytest.raises(BUNDLE.NodeBundleError, match="rareburden"):
        BUNDLE.build_node_bundle(tmp_path / "bundle.zip", other)
