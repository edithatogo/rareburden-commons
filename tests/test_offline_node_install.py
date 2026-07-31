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


def test_offline_install_constructs_network_disabled_commands(tmp_path: Path) -> None:
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
            json.dumps({"output_fingerprint": "sha256:" + "0" * 64, "rows": 1})
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
