from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest


def _load_script() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts/check_offline_node_install.py"
    spec = importlib.util.spec_from_file_location("check_offline_node_install", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OFFLINE = _load_script()


def test_offline_install_constructs_network_disabled_commands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PYTHONPATH", str(tmp_path / "source-checkout"))
    monkeypatch.setenv("PYTHONHOME", str(tmp_path / "other-runtime"))
    node = tmp_path / "rareburden-1-py3-none-any.whl"
    node.write_bytes(b"node")
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    dependency = wheelhouse / "dependency-1-py3-none-any.whl"
    dependency.write_bytes(b"dependency")
    calls: list[tuple[list[str], Path | None, dict[str, str]]] = []

    def runner(
        arguments: list[str], cwd: Path | None, environment: dict[str, str]
    ) -> subprocess.CompletedProcess[str]:
        calls.append((arguments, cwd, environment))
        stdout = (
            json.dumps({"output_fingerprint": OFFLINE.EXPECTED_OUTPUT_FINGERPRINT, "rows": 1})
            if Path(arguments[0]).stem == "python"
            else ""
        )
        return subprocess.CompletedProcess(arguments, 0, stdout=stdout, stderr="")

    receipt = OFFLINE.check_offline_install(
        node_wheel=node,
        wheelhouse=wheelhouse,
        python_version="3.13",
        runner=runner,
    )
    install = calls[1]
    assert "--offline" in install[0]
    assert "--no-index" in install[0]
    assert install[2]["UV_OFFLINE"] == "1"
    assert install[2]["PIP_NO_INDEX"] == "1"
    assert "PYTHONPATH" not in install[2]
    assert "PYTHONHOME" not in install[2]
    assert calls[-1][0][1:3] == ["-I", "-c"]
    assert receipt["network_disabled"] is True
    assert receipt["dependency_wheel_count"] == 1
    assert set(receipt["artifact_sha256"]) == {node.name, dependency.name}


def test_offline_install_rejects_missing_or_empty_inputs(tmp_path: Path) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    with pytest.raises(OFFLINE.OfflineInstallError, match="node wheel"):
        OFFLINE.check_offline_install(
            node_wheel=tmp_path / "missing.whl",
            wheelhouse=wheelhouse,
            python_version="3.13",
        )
    node = tmp_path / "rareburden.whl"
    node.write_bytes(b"node")
    with pytest.raises(OFFLINE.OfflineInstallError, match="no dependency"):
        OFFLINE.check_offline_install(
            node_wheel=node,
            wheelhouse=wheelhouse,
            python_version="3.13",
        )


def test_offline_install_rejects_symlinks_and_node_in_wheelhouse(tmp_path: Path) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    node = wheelhouse / "rareburden.whl"
    node.write_bytes(b"node")
    with pytest.raises(OFFLINE.OfflineInstallError, match="must not also appear"):
        OFFLINE.check_offline_install(
            node_wheel=node,
            wheelhouse=wheelhouse,
            python_version="3.13",
        )
    linked = tmp_path / "linked.whl"
    linked.symlink_to(node)
    with pytest.raises(OFFLINE.OfflineInstallError, match="safe local wheel"):
        OFFLINE.check_offline_install(
            node_wheel=linked,
            wheelhouse=wheelhouse,
            python_version="3.13",
        )


@pytest.fixture
def offline_inputs(tmp_path: Path) -> tuple[Path, Path]:
    node = tmp_path / "rareburden-1-py3-none-any.whl"
    node.write_bytes(b"node")
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    (wheelhouse / "dependency-1-py3-none-any.whl").write_bytes(b"dependency")
    return node, wheelhouse


@pytest.mark.parametrize(
    "output",
    [
        "not JSON",
        "null",
        "[]",
        "{}",
        json.dumps({"output_fingerprint": OFFLINE.EXPECTED_OUTPUT_FINGERPRINT, "rows": True}),
        json.dumps({"output_fingerprint": OFFLINE.EXPECTED_OUTPUT_FINGERPRINT, "rows": 0}),
        json.dumps({"output_fingerprint": "not-a-fingerprint", "rows": 1}),
        json.dumps({"output_fingerprint": "sha256:" + "0" * 64, "rows": 1}),
        json.dumps(
            {"output_fingerprint": OFFLINE.EXPECTED_OUTPUT_FINGERPRINT, "rows": 1, "extra": 1}
        ),
    ],
)
def test_offline_install_rejects_invalid_installed_result(
    offline_inputs: tuple[Path, Path], output: str
) -> None:
    node, wheelhouse = offline_inputs

    def runner(arguments, cwd, environment):
        return subprocess.CompletedProcess(arguments, 0, stdout=output, stderr="")

    with pytest.raises(OFFLINE.OfflineInstallError, match="installed-node check"):
        OFFLINE.check_offline_install(
            node_wheel=node, wheelhouse=wheelhouse, python_version="3.13", runner=runner
        )


@pytest.mark.parametrize("target", ["node", "dependency"])
def test_offline_install_rejects_artifact_changes_during_commands(
    offline_inputs: tuple[Path, Path], target: str
) -> None:
    node, wheelhouse = offline_inputs
    artifact = node if target == "node" else next(wheelhouse.iterdir())

    def runner(arguments, cwd, environment):
        artifact.write_bytes(b"changed after preflight")
        output = json.dumps({"output_fingerprint": OFFLINE.EXPECTED_OUTPUT_FINGERPRINT, "rows": 1})
        return subprocess.CompletedProcess(arguments, 0, stdout=output, stderr="")

    with pytest.raises(OFFLINE.OfflineInstallError, match="artifacts changed"):
        OFFLINE.check_offline_install(
            node_wheel=node, wheelhouse=wheelhouse, python_version="3.13", runner=runner
        )


def test_offline_install_rejects_duplicate_receipt_identity_before_commands(
    offline_inputs: tuple[Path, Path],
) -> None:
    node, wheelhouse = offline_inputs
    (wheelhouse / node.name).write_bytes(b"different node bytes")

    def forbidden_runner(*args):
        pytest.fail("duplicate receipt identity reached a subprocess")

    with pytest.raises(OFFLINE.OfflineInstallError, match="filenames must be distinct"):
        OFFLINE.check_offline_install(
            node_wheel=node,
            wheelhouse=wheelhouse,
            python_version="3.13",
            runner=forbidden_runner,
        )


@pytest.mark.parametrize("failure_step", [0, 1, 2, 3])
def test_offline_install_stops_on_failed_subprocess(
    offline_inputs: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, failure_step: int
) -> None:
    node, wheelhouse = offline_inputs
    calls = []

    def failed_command(arguments, **kwargs):
        assert kwargs["check"] is True
        calls.append(arguments)
        if len(calls) == failure_step + 1:
            raise subprocess.CalledProcessError(1, arguments, stderr="synthetic failure")
        return subprocess.CompletedProcess(arguments, 0, stdout="", stderr="")

    monkeypatch.setattr(OFFLINE.subprocess, "run", failed_command)
    with pytest.raises(OFFLINE.OfflineInstallError, match="offline command failed"):
        OFFLINE.check_offline_install(
            node_wheel=node, wheelhouse=wheelhouse, python_version="3.13"
        )
    assert len(calls) == failure_step + 1
