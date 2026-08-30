"""Mutation checks on retained evidence; no analytical execution or output copies."""

import copy
import io
import json
import tarfile
from pathlib import Path

import pytest

from scripts import check_track003_reference_closeout as check

ROOT = Path(__file__).resolve().parents[1]


def documents():
    return (
        json.loads((ROOT / check.RECEIPT).read_bytes()),
        (ROOT / check.DECISION).read_bytes(),
        {name: (ROOT / check.OUTPUT_DIRECTORY / name).read_bytes() for name in check.OUTPUT_HASHES},
    )


def test_retained_package_is_valid_without_simulation(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Validation must never execute analysis")

    monkeypatch.setattr("scripts.track003_reference_package.simulate", forbidden)
    check.validate(ROOT)


def test_historical_snapshot_is_platform_independent_and_source_changes_are_allowed(monkeypatch):
    manifest = json.loads((ROOT / check.MANIFEST).read_bytes())
    original_read = Path.read_bytes

    def reject_current_sources(path):
        if path.is_relative_to(ROOT) and path.relative_to(ROOT).as_posix() in manifest["files"]:
            raise AssertionError("Current source files must not be consulted or frozen")
        return original_read(path)

    monkeypatch.setattr(Path, "read_bytes", reject_current_sources)
    check.validate(ROOT)
    files = check.validate_snapshot((ROOT / check.SNAPSHOT).read_bytes(), manifest["files"])
    assert len(files) == 74
    assert all("\\" not in name for name in files)


def test_snapshot_byte_drift_is_rejected():
    with pytest.raises(ValueError, match="snapshot differs"):
        check.validate_snapshot(b"changed archive", {})


@pytest.mark.parametrize("name", ["../escape.py", "/absolute.py", "src\\windows.py"])
def test_unsafe_snapshot_member_is_rejected(monkeypatch, name):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        member = tarfile.TarInfo(name)
        archive.addfile(member, io.BytesIO())
    content = buffer.getvalue()
    monkeypatch.setattr(check, "SNAPSHOT_SHA", check.digest(content))
    with pytest.raises(ValueError, match="unsafe historical member path"):
        check.validate_snapshot(content, {name: check.digest(b"")})


@pytest.mark.parametrize(
    "mutation",
    [
        "candidate",
        "decision",
        "inventory",
        "bytes",
        "reproduction_hash",
        "run_count",
        "checkout",
        "exit",
        "claim",
        "comparison",
        "output_path",
    ],
)
def test_receipt_mutations_fail(mutation):
    receipt, decision, outputs = documents()
    receipt = copy.deepcopy(receipt)
    if mutation == "candidate":
        receipt["candidate"]["tree"] = "0" * 40
    elif mutation == "decision":
        decision += b" "
    elif mutation == "inventory":
        outputs.pop("reference-report.md")
    elif mutation == "bytes":
        outputs["reference-report.md"] += b" "
    elif mutation == "reproduction_hash":
        receipt["runs"][1]["receipt"]["output_sha256"]["reference-report.md"] = "0" * 64
    elif mutation == "run_count":
        receipt["runs"].pop()
    elif mutation == "checkout":
        receipt["runs"][1]["checkout_id"] = receipt["runs"][0]["checkout_id"]
    elif mutation == "exit":
        receipt["runs"][1]["exit_code"] = 1
    elif mutation == "claim":
        receipt["claims"]["empirical_validity"] = True
    elif mutation == "comparison":
        receipt["comparison"]["extra_executions"] = 1
    elif mutation == "output_path":
        receipt["output_directory"] = "elsewhere"
    with pytest.raises(ValueError):
        check.validate_documents(receipt, decision, outputs)
