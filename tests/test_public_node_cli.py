"""Installed runner command tests using invented inputs only."""

import hashlib
import sys
from types import SimpleNamespace

import pytest

from rareburden import public_node_cli
from rareburden.node import NodeExportError
from rareburden.public_delivery import stage_results
from rareburden.public_node import prepare_public_records


def test_huge_numeric_code_fails_without_overflow():
    with pytest.raises(NodeExportError, match="finite numeric"):
        prepare_public_records([{"SEQN": 1, "DIQ010": 10**500}], dataset="nhanes")


def test_recovery_does_not_load_data(tmp_path, monkeypatch, capsys):
    stage_results(tmp_path, {"example": {"count": 10}})
    monkeypatch.setattr(sys, "argv", ["runner", "--output", str(tmp_path), "--recover"])

    def forbidden(*args):
        raise AssertionError("recovery loaded an analysis dependency")

    monkeypatch.setattr(public_node_cli.importlib, "import_module", forbidden)
    public_node_cli.main()
    assert "no analysis rerun" in capsys.readouterr().out


def test_source_required(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["runner", "--output", str(tmp_path)])
    with pytest.raises(SystemExit) as error:
        public_node_cli.main()
    assert error.value.code == 2


def test_source_hash_rejected_before_output(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.write_bytes(b"not-the-pinned-data")
    output = tmp_path / "output"
    monkeypatch.setattr(public_node_cli, "SOURCES", {"uci": ("source", "0" * 64)})
    monkeypatch.setattr(public_node_cli.importlib, "import_module", lambda _: SimpleNamespace())
    monkeypatch.setattr(
        sys, "argv", ["runner", "--source-root", str(tmp_path), "--output", str(output)]
    )
    with pytest.raises(ValueError, match="source hash"):
        public_node_cli.main()
    assert not output.exists()


@pytest.mark.parametrize("survey", [False, True])
def test_verified_bytes_used_for_descriptive_run(tmp_path, monkeypatch, survey):
    bodies = {"uci": b"uci", "nhanes": b"nhanes"}
    sources = {}
    for dataset, body in bodies.items():
        (tmp_path / dataset).write_bytes(body)
        sources[dataset] = (dataset, hashlib.sha256(body).hexdigest())

    def read_parquet(stream):
        body = stream.read()
        if body == b"uci":
            rows = [
                {"encounter_id": str(i), "patient_nbr": "1", "readmitted": "NO"} for i in range(10)
            ]
        elif body == b"nhanes":
            rows = [{"SEQN": i + 1, "DIQ010": 1 if i < 5 else 2} for i in range(10)]
        else:
            rows = [
                {
                    "SEQN": i + 1,
                    "RIDAGEYR": 20,
                    "WTINT2YR": 1,
                    "SDMVSTRA": 1,
                    "SDMVPSU": 1 if i < 5 else 2,
                }
                for i in range(10)
            ]
        return SimpleNamespace(to_dict=lambda _: rows)

    monkeypatch.setattr(public_node_cli, "SOURCES", sources)
    monkeypatch.setattr(
        public_node_cli.importlib,
        "import_module",
        lambda _: SimpleNamespace(read_parquet=read_parquet),
    )
    output = tmp_path / "output"
    (tmp_path / "demo").write_bytes(b"demo")
    monkeypatch.setattr(
        public_node_cli, "DEMO_SOURCE", ("demo", hashlib.sha256(b"demo").hexdigest())
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["runner", "--source-root", str(tmp_path), "--output", str(output)]
        + (["--survey"] if survey else []),
    )
    public_node_cli.main()
    assert (output / "results.json").read_bytes() == (output / "results.staged.json").read_bytes()
