from __future__ import annotations

import json
import tarfile
import zipfile
from pathlib import Path

from scripts.build_distributions import _canonicalise_sdist
from scripts.check_built_package import PackageCheckError, inspect_sdist, inspect_wheel
from scripts.check_github_workflows import validate_workflow, validate_workflows
from scripts.check_schemas import validate_schemas

PIN = "a" * 40


def _workflow(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_workflow_policy_accepts_pinned_least_privilege_workflow(tmp_path: Path) -> None:
    path = _workflow(
        tmp_path / "ci.yml",
        f"""name: ci
on: [push]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@{PIN}
        with:
          persist-credentials: false
      - run: echo safe
""",
    )
    assert validate_workflow(path) == []
    assert validate_workflows([path]) == []


def test_workflow_policy_rejects_mutable_actions_and_unsafe_context(tmp_path: Path) -> None:
    path = _workflow(
        tmp_path / "unsafe.yml",
        """name: unsafe
on:
  pull_request_target:
permissions: write-all
jobs:
  bad:
    runs-on: ubuntu-latest
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
      - run: echo '${{ github.event.pull_request.title }}'
""",
    )
    errors = validate_workflow(path)
    assert any("dangerous trigger" in error for error in errors)
    assert any("full 40-character" in error for error in errors)
    assert any("persist-credentials" in error for error in errors)
    assert any("timeout-minutes" in error for error in errors)
    assert any("untrusted GitHub context" in error for error in errors)
    assert any("write-all" in error for error in errors)


def test_workflow_policy_reports_malformed_and_missing_jobs(tmp_path: Path) -> None:
    malformed = _workflow(tmp_path / "bad.yml", "jobs: [")
    empty = _workflow(tmp_path / "empty.yml", "name: empty\non: push\npermissions: {}\njobs: {}\n")
    assert "cannot parse" in validate_workflow(malformed)[0]
    assert any("non-empty mapping" in item for item in validate_workflow(empty))


def test_schema_collection_check_detects_duplicates_and_invalid_ids(tmp_path: Path) -> None:
    valid = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://rareburden.org/schemas/example/1",
        "type": "object",
    }
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    third = tmp_path / "third.json"
    first.write_text(json.dumps(valid))
    second.write_text(json.dumps(valid))
    invalid = {**valid, "$id": "relative", "type": "not-a-json-schema-type"}
    third.write_text(json.dumps(invalid))
    errors = validate_schemas([first, second, third])
    assert any("duplicate $id" in error for error in errors)
    assert any("absolute HTTPS" in error for error in errors)
    assert any("invalid Draft 2020-12" in error for error in errors)


def _write_wheel(path: Path, *, forbidden: bool = False) -> None:
    import base64
    import csv
    import hashlib
    import io

    version = "0.3.0rc2"
    dist_info = f"rareburden-{version}.dist-info"
    metadata = (
        "Metadata-Version: 2.4\n"
        "Name: rareburden\n"
        f"Version: {version}\n"
        "License-Expression: Apache-2.0\n\n"
    ).encode()
    wheel = (
        b"Wheel-Version: 1.0\n"
        b"Generator: rareburden-test\n"
        b"Root-Is-Purelib: true\n"
        b"Tag: py3-none-any\n\n"
    )
    required = {
        "catalog/data_sources.yml",
        "catalog/initiatives.yml",
        "conductor/roadmap.yml",
        "schemas/release-manifest.schema.json",
        "schemas/node-input.schema.json",
        "schemas/node-output.schema.json",
        "schemas/node-execution-manifest.schema.json",
        "schemas/node-disclosure-policy.schema.json",
        "schemas/transformation-run.schema.json",
        "examples/node-input-synthetic.yml",
        "examples/node-output-synthetic.yml",
        "docs/federated-node-004-operator-guide.md",
        "examples/fixtures/orphadata-synthetic.xml",
        "pyproject.toml",
        "uv.lock",
    }
    prefix = "rareburden/resources/repository/"
    members: dict[str, bytes] = {
        "rareburden/__init__.py": b"",
        "rareburden/cli.py": b"",
        "rareburden/py.typed": b"",
        f"{dist_info}/METADATA": metadata,
        f"{dist_info}/WHEEL": wheel,
    }
    runtime_records = []
    for logical in sorted(required):
        data = f"fixture:{logical}\n".encode()
        members[prefix + logical] = data
        runtime_records.append(
            {
                "path": logical,
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
            }
        )
    runtime_manifest = (
        json.dumps(
            {
                "schema_version": "1.0.0",
                "purpose": "test fixture",
                "file_count": len(runtime_records),
                "files": runtime_records,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode()
    members[prefix + "runtime-assets.json"] = runtime_manifest
    if forbidden:
        members["tests/fixtures/private.db"] = b"secret"

    record_name = f"{dist_info}/RECORD"
    rows = []
    for name, data in sorted(members.items()):
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
        rows.append([name, f"sha256={digest}", str(len(data))])
    rows.append([record_name, "", ""])
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(rows)
    members[record_name] = buffer.getvalue().encode()

    with zipfile.ZipFile(path, "w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)


def test_wheel_inspection_accepts_expected_metadata_and_rejects_forbidden(tmp_path: Path) -> None:
    valid = tmp_path / "valid.whl"
    invalid = tmp_path / "invalid.whl"
    _write_wheel(valid)
    _write_wheel(invalid, forbidden=True)
    inspect_wheel(valid, expected_name="rareburden", expected_version="0.3.0rc2")
    try:
        inspect_wheel(invalid, expected_name="rareburden", expected_version="0.3.0rc2")
    except PackageCheckError as exc:
        assert "forbidden" in str(exc)
    else:  # pragma: no cover - assertion guard
        raise AssertionError("forbidden wheel content was accepted")


def test_sdist_inspection_rejects_symlink(tmp_path: Path) -> None:
    archive_path = tmp_path / "bad.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        info = tarfile.TarInfo("rareburden-0.3.0rc1/link")
        info.type = tarfile.SYMTYPE
        info.linkname = "/etc/passwd"
        archive.addfile(info)
    try:
        inspect_sdist(archive_path)
    except PackageCheckError as exc:
        assert "unsafe member" in str(exc)
    else:  # pragma: no cover - assertion guard
        raise AssertionError("unsafe source-distribution member was accepted")


def _write_noncanonical_sdist(path: Path, *, reverse: bool, member_mtime: int, uid: int) -> None:
    records = [
        ("rareburden-0.3.0rc2/", True, b""),
        ("rareburden-0.3.0rc2/README.md", False, b"reference\n"),
        ("rareburden-0.3.0rc2/src/module.py", False, b"VALUE = 1\n"),
    ]
    if reverse:
        records.reverse()
    with tarfile.open(path, "w:gz") as archive:
        for name, is_directory, data in records:
            info = tarfile.TarInfo(name)
            info.mtime = member_mtime
            info.uid = uid
            info.gid = uid
            info.uname = f"user-{uid}"
            info.gname = f"group-{uid}"
            if is_directory:
                info.type = tarfile.DIRTYPE
                info.mode = 0o700
                archive.addfile(info)
            else:
                info.size = len(data)
                info.mode = 0o600
                archive.addfile(info, __import__("io").BytesIO(data))


def test_sdist_canonicalisation_normalises_order_and_archive_metadata(tmp_path: Path) -> None:
    first = tmp_path / "first.tar.gz"
    second = tmp_path / "second.tar.gz"
    _write_noncanonical_sdist(first, reverse=False, member_mtime=100, uid=1000)
    _write_noncanonical_sdist(second, reverse=True, member_mtime=200, uid=2000)

    epoch = 1_760_000_000
    _canonicalise_sdist(first, source_date_epoch=epoch)
    _canonicalise_sdist(second, source_date_epoch=epoch)

    assert first.read_bytes() == second.read_bytes()
    with tarfile.open(first, "r:gz") as archive:
        members = archive.getmembers()
    assert [member.name for member in members] == sorted(member.name for member in members)
    assert all(member.mtime == epoch for member in members)
    assert all(member.uid == 0 and member.gid == 0 for member in members)
    assert all(member.uname == "" and member.gname == "" for member in members)
