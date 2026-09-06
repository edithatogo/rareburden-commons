"""Current-platform installed-wheel rehearsal, with enforced macOS network denial.

All mutable evidence and real input processing stay in a new external directory.
This does not approve a release, clinical analysis or custodian deployment.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import importlib.metadata
import io
import json
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

SOURCES = {
    "uci": (
        "uci-diabetes-130-us-hospitals/data/encounters.parquet",
        "cf435350273822ed4a3193e8dfd22e38bbf264839073c353cf2dda2b1fab1cb9",
    ),
    "nhanes": (
        "nhanes-2021-2023-diabetes/data/DIQ_L.parquet",
        "72404c82dcd9d9fab2233757e4b4cc97b3b2bc769e25a9d390b1d4fe2eb9242c",
    ),
}
PROFILE = "(version 1) (allow default) (deny network*)"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lock_entries(body: str) -> dict[str, tuple[str, str]]:
    """Deliberately narrow format: one exact version and wheel hash per line."""
    entries = {}
    for line in body.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        match = re.fullmatch(r"([a-z0-9-]+)==([0-9A-Za-z.]+) --hash=sha256:([a-f0-9]{64})", line)
        if match is None or match[1] in entries:
            raise ValueError("invalid or duplicate locked requirement")
        entries[match[1]] = (match[2], match[3])
    if not entries:
        raise ValueError("empty runtime lock")
    return entries


def require_network_denied() -> None:
    """An unavailable endpoint is not evidence of sandbox enforcement."""
    try:
        with socket.socket() as connection:
            connection.settimeout(1)
            connection.connect(("127.0.0.1", 9))
    except OSError as exc:
        if exc.errno == errno.EPERM:
            return
        raise RuntimeError("network probe did not prove EPERM denial") from None
    raise RuntimeError("network access was not denied")


def run(command: list[str], output: Path, name: str) -> None:
    result = subprocess.run(
        command,
        cwd=output,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        check=False,
        timeout=240,
    )
    (output / f"{name}.log").write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"{name} failed; inspect the external log")


def probe(source_root: Path, output: Path) -> None:
    import pandas as pd
    import pyarrow

    import rareburden.public_delivery as public_delivery
    import rareburden.public_node as public_node
    import rareburden.public_node_cli as public_node_cli
    import rareburden.public_survey as public_survey
    from rareburden.node_policy_store import DurableNodePolicyStore

    require_network_denied()
    modules = (pd, pyarrow, public_node, public_node_cli, public_survey, public_delivery)
    if sys.prefix == sys.base_prefix or any(
        not Path(module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
        for module in modules
    ):
        raise RuntimeError("imports do not originate in the clean installed environment")
    inputs = {}
    for dataset, (relative, expected) in SOURCES.items():
        body = (source_root / relative).read_bytes()
        if hashlib.sha256(body).hexdigest() != expected:
            raise ValueError("pinned public source hash mismatch")
        inputs[dataset] = body
    timestamp = datetime.now(UTC).isoformat()
    hashes = {}
    with DurableNodePolicyStore(output / "policy.sqlite3") as store:
        policy = store.register_policy(
            {
                "schema_version": "0.1.0",
                "policy_id": "public-count-policy-v1",
                "minimum_cell_count": 5,
                "max_queries_per_overlap_group": 1,
                "allowed_dimension_fields": ["group"],
                "participant_fields": ["person_id"],
                "export_mode": "aggregate_only",
            },
            recorded_at=timestamp,
        )
        for dataset, body in inputs.items():
            result = public_node.run_public_counts(
                pd.read_parquet(io.BytesIO(body)).to_dict("records"),
                dataset=dataset,
                source_sha256=SOURCES[dataset][1],
                store=store,
                policy_id=policy.policy_id,
                policy_sha256=policy.content_sha256,
                recorded_at=timestamp,
            )
            claimed = result.pop("output_sha256")
            actual = hashlib.sha256(
                json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            if claimed != actual or result["population_estimate"] is not False:
                raise RuntimeError("unexpected descriptive result contract")
            hashes[dataset] = actual
        if store.verify() != (1, 2):
            raise RuntimeError("unexpected durable reservation count")
    cli_result = output / "cli-survey" / "results.json"
    with DurableNodePolicyStore(output / "cli-survey" / "policy.sqlite3") as cli_store:
        if cli_store.verify() != (1, 3):
            raise RuntimeError("unexpected installed CLI reservation count")
    cli_bundle = json.loads(cli_result.read_text())
    if set(cli_bundle) != {"uci", "nhanes", "nhanes_survey"}:
        raise RuntimeError("installed CLI did not return the requested survey bundle")
    cli_hashes = {}
    for name, result in cli_bundle.items():
        claimed = result.pop("output_sha256")
        actual = hashlib.sha256(
            json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if claimed != actual:
            raise RuntimeError("installed CLI result digest mismatch")
        cli_hashes[name] = actual
    if (output / "cli-survey" / "results.sha256").read_text().strip() != digest(cli_result):
        raise RuntimeError("installed CLI delivery digest mismatch")
    receipt = {
        "recorded_at": timestamp,
        "network_probe": "EPERM",
        "python": sys.version,
        "python_executable_sha256": digest(Path(sys.executable)),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "imports_from_clean_venv": True,
        "installed_versions": dict(
            sorted(
                (dist.metadata["Name"], dist.version) for dist in importlib.metadata.distributions()
            )
        ),
        "module_sha256": {module.__name__: digest(Path(module.__file__)) for module in modules},
        "source_sha256": {key: value[1] for key, value in SOURCES.items()},
        "descriptive_output_sha256": hashes,
        "verified_store_counts": [1, 2],
        "population_estimate": False,
        "custodian_deployment": False,
        "installed_cli_survey": {
            "result_sha256": digest(cli_result),
            "verified_embedded_sha256": cli_hashes,
            "verified_store_counts": [1, 3],
            "recovery_preserved_result": True,
            "demo_source_sha256": public_node_cli.DEMO_SOURCE[1],
            "scope": "experimental adult survey candidate; no clinical validation",
        },
    }
    (output / "computation.json").write_text(json.dumps(receipt, indent=2) + "\n")


def worker(output: Path, source_root: Path) -> None:
    require_network_denied()
    run([sys.executable, "-I", "-m", "venv", str(output / "venv")], output, "venv")
    python = str(output / "venv/bin/python")
    run(
        [
            python,
            "-I",
            "-m",
            "pip",
            "--isolated",
            "install",
            "--no-cache-dir",
            "--no-index",
            "--only-binary=:all:",
            "--require-hashes",
            "--find-links",
            str(output / "wheelhouse"),
            "-r",
            str(output / "installation.txt"),
        ],
        output,
        "install",
    )
    run([python, "-I", "-m", "pip", "--isolated", "check"], output, "pip-check")
    run(
        [
            python,
            "-I",
            "-m",
            "rareburden.public_node_cli",
            "--survey",
            "--source-root",
            str(source_root),
            "--output",
            str(output / "cli-survey"),
        ],
        output,
        "cli-survey",
    )
    before = digest(output / "cli-survey" / "results.json")
    run(
        [
            python,
            "-I",
            "-m",
            "rareburden.public_node_cli",
            "--recover",
            "--output",
            str(output / "cli-survey"),
        ],
        output,
        "cli-recovery",
    )
    if digest(output / "cli-survey" / "results.json") != before:
        raise RuntimeError("recovery changed delivered result")
    run(
        [
            python,
            "-I",
            str(output / "verify.py"),
            "--probe",
            "--source-root",
            str(source_root),
            "--output",
            str(output),
        ],
        output,
        "computation",
    )


def verify(args: argparse.Namespace) -> None:
    if (
        platform.system() != "Darwin"
        or platform.machine() != "arm64"
        or sys.version_info[:2] != (3, 13)
    ):
        raise RuntimeError("this proof requires macOS arm64 CPython 3.13")
    sandbox = shutil.which("sandbox-exec")
    if sandbox is None:
        raise RuntimeError("sandbox-exec unavailable; no offline proof claimed")
    lock_body = args.lock.read_bytes()
    entries = lock_entries(lock_body.decode())
    if "rareburden" in entries:
        raise ValueError("node wheel must be separately exact-bound")
    if digest(args.node_wheel) != args.expected_node_sha256:
        raise ValueError("node wheel hash mismatch")
    name_parts = args.node_wheel.name.split("-")
    if len(name_parts) != 5 or name_parts[0] != "rareburden":
        raise ValueError("unexpected node wheel filename")
    entries["rareburden"] = (name_parts[1], args.expected_node_sha256)
    selected = {}
    for name, (version, expected) in entries.items():
        candidates = (
            [args.node_wheel]
            if name == "rareburden"
            else list(args.wheelhouse.glob(f"{name.replace('-', '_')}-{version}-*.whl"))
        )
        if len(candidates) != 1 or digest(candidates[0]) != expected:
            raise ValueError("missing, ambiguous or changed locked wheel")
        selected[name] = candidates[0]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "wheelhouse").mkdir()
    for name, path in selected.items():
        destination = output / "wheelhouse" / path.name
        shutil.copyfile(path, destination)
        if digest(destination) != entries[name][1]:
            raise ValueError("wheel changed during staging")
    shutil.copyfile(__file__, output / "verify.py")
    (output / "dependencies.txt").write_bytes(lock_body)
    (output / "installation.txt").write_text(
        "".join(
            f"{name}=={version} --hash=sha256:{sha}\n"
            for name, (version, sha) in sorted(entries.items())
        )
    )
    run(
        [
            sandbox,
            "-p",
            PROFILE,
            sys.executable,
            "-I",
            str(output / "verify.py"),
            "--worker",
            "--source-root",
            str(args.source_root.resolve()),
            "--output",
            str(output),
        ],
        output,
        "sandbox",
    )
    receipt = json.loads((output / "computation.json").read_text())
    for name, (version, expected) in entries.items():
        if digest(output / "wheelhouse" / selected[name].name) != expected:
            raise ValueError("locked wheel changed during installation proof")
        versions = {
            key.lower().replace("_", "-"): value
            for key, value in receipt["installed_versions"].items()
        }
        if versions.get(name) != version:
            raise ValueError("installed version differs from runtime lock")
    receipt.update(
        {
            "dependency_lock_sha256": hashlib.sha256(lock_body).hexdigest(),
            "installation_lock_sha256": digest(output / "installation.txt"),
            "verifier_sha256": digest(output / "verify.py"),
            "sandbox_profile": PROFILE,
            "node_wheel_sha256": args.expected_node_sha256,
            "wheel_sha256": {
                path.name: digest(path) for path in sorted((output / "wheelhouse").iterdir())
            },
            "installation": "new venv; isolated pip; no cache; no index; hashes required",
        }
    )
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("PASS: clean installed public counts with network denied; external receipt retained.")


def self_test() -> None:
    from unittest.mock import patch

    good = "pandas==2.3.3 --hash=sha256:" + "a" * 64
    assert lock_entries(good)["pandas"] == ("2.3.3", "a" * 64)
    for bad in ("", "pandas>=2", good + "\n" + good, good[:-1], "-r other.txt"):
        try:
            lock_entries(bad)
        except ValueError:
            continue
        raise AssertionError("unsafe lock accepted")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        path = root / "wheel"
        path.write_bytes(b"before")
        before = digest(path)
        path.write_bytes(b"after")
        assert digest(path) != before
        lock = root / "dependencies.txt"
        lock.write_text(good)
        node = root / "rareburden-0.3.0rc2-py3-none-any.whl"
        node.write_bytes(b"invented wheel for preflight rejection only")
        args = argparse.Namespace(
            lock=lock,
            node_wheel=node,
            expected_node_sha256="b" * 64,
            wheelhouse=root,
            output=root / "must-not-exist",
            source_root=root,
        )
        with (
            patch.object(platform, "system", return_value="Darwin"),
            patch.object(platform, "machine", return_value="arm64"),
            patch.object(sys, "version_info", (3, 13, 0)),
            patch.object(shutil, "which", return_value="/usr/bin/sandbox-exec"),
        ):
            for expected_message in ("node wheel hash mismatch", "missing, ambiguous"):
                try:
                    verify(args)
                except ValueError as exc:
                    assert expected_message in str(exc)
                else:
                    raise AssertionError("unsafe wheel inventory accepted")
                assert not args.output.exists()
                args.expected_node_sha256 = digest(node)
    print("PASS: lock parser, byte-change, wrong-node and missing-wheel rejection checks")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--wheelhouse", type=Path)
    parser.add_argument("--node-wheel", type=Path)
    parser.add_argument("--expected-node-sha256")
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--output", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    mode.add_argument("--probe", action="store_true", help=argparse.SUPPRESS)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.source_root is None or args.output is None:
        parser.error("--source-root and --output required")
    elif args.worker:
        worker(args.output, args.source_root)
    elif args.probe:
        probe(args.source_root, args.output)
    else:
        if any(
            value is None
            for value in (
                args.lock,
                args.wheelhouse,
                args.node_wheel,
                args.expected_node_sha256,
            )
        ):
            parser.error("--lock, --wheelhouse, --node-wheel and --expected-node-sha256 required")
        verify(args)


if __name__ == "__main__":
    main()
