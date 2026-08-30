"""Mutation checks on retained evidence; no analytical execution or output copies."""

import copy
import json
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
