"""Crash-recoverable local delivery of already disclosure-checked results.

Trusted owner-controlled directory required. Hashes detect accidental damage,
not malicious replacement by its owner. Recovery never recomputes an analysis.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


def _sync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _exclusive_write(path: Path, body: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())


def create_run_directory(directory: Path) -> None:
    """Create one new run under an existing trusted parent and sync its entry."""
    directory.mkdir(exist_ok=False)
    _sync_directory(directory.parent)


def stage_results(directory: Path, results: dict[str, Any]) -> str:
    """Durably stage once; a partial stage is deliberately not recoverable."""
    body = json.dumps(results, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    digest = hashlib.sha256(body).hexdigest()
    _exclusive_write(directory / "results.staged.json", body)
    _sync_directory(directory)
    _exclusive_write(directory / "results.sha256", (digest + "\n").encode())
    _sync_directory(directory)
    return digest


def recover_results(directory: Path) -> str:
    """Publish the exact durable stage without overwriting or spending again.

    A crash before the digest was persisted requires operator investigation,
    not a rerun. Retain the stage and digest as recovery evidence after success.
    POSIX local filesystem durability only; network filesystems are unqualified.
    """
    staged = directory / "results.staged.json"
    receipt = directory / "results.sha256"
    destination = directory / "results.json"
    for path in (staged, receipt, destination):
        if path.is_symlink():
            raise ValueError("delivery paths must not be symbolic links")
    body = staged.read_bytes()
    digest = hashlib.sha256(body).hexdigest()
    if receipt.read_bytes() != (digest + "\n").encode():
        raise ValueError("staged result digest mismatch; do not recompute")
    decoded = json.loads(body)
    if not isinstance(decoded, dict) or not decoded:
        raise ValueError("staged result must be a nonempty object")
    try:
        # Atomic no-overwrite publication on the same filesystem.
        os.link(staged, destination)
    except FileExistsError:
        if destination.read_bytes() != body:
            raise ValueError("existing result differs; do not overwrite") from None
    _sync_directory(directory)
    return digest
