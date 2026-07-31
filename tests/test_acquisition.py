from __future__ import annotations

import contextlib
import hashlib
import http.server
import threading
from collections.abc import Iterator
from functools import partial
from pathlib import Path

import pytest

from rareburden.acquisition import AcquisitionError, DownloadPolicy, download_public_artifact


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


@contextlib.contextmanager
def local_server(directory: Path) -> Iterator[str]:
    handler = partial(_QuietHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_network_access_requires_explicit_opt_in(tmp_path: Path) -> None:
    with pytest.raises(AcquisitionError, match="disabled"):
        download_public_artifact(
            source_id="fixture",
            release_id="r1",
            url="https://example.org/fixture.csv",
            destination=tmp_path / "fixture.csv",
            expected_sha256="0" * 64,
        )


def test_pinned_download_is_atomic_and_manifested(tmp_path: Path) -> None:
    served = tmp_path / "served"
    served.mkdir()
    payload = b"country,value\nAUS,1\n"
    (served / "fixture.csv").write_bytes(payload)
    expected = hashlib.sha256(payload).hexdigest()
    destination = tmp_path / "cache" / "fixture.csv"

    with local_server(served) as base_url:
        manifest = download_public_artifact(
            source_id="fixture-source",
            release_id="r1",
            url=f"{base_url}/fixture.csv",
            destination=destination,
            expected_sha256=expected,
            policy=DownloadPolicy(
                allow_insecure_http=True,
                allow_private_network=True,
                retries=0,
            ),
            allow_network=True,
        )

    assert destination.read_bytes() == payload
    assert manifest["artifact"]["sha256"] == expected
    assert manifest["pinning"]["status"] == "verified"
    assert not list(destination.parent.glob(".*.partial"))


def test_checksum_failure_preserves_existing_destination(tmp_path: Path) -> None:
    served = tmp_path / "served"
    served.mkdir()
    (served / "fixture.txt").write_text("new bytes", encoding="utf-8")
    destination = tmp_path / "fixture.txt"
    destination.write_text("trusted old bytes", encoding="utf-8")

    with local_server(served) as base_url, pytest.raises(AcquisitionError, match="Checksum"):
        download_public_artifact(
            source_id="fixture-source",
            release_id="r2",
            url=f"{base_url}/fixture.txt",
            destination=destination,
            expected_sha256="0" * 64,
            policy=DownloadPolicy(
                allow_insecure_http=True,
                allow_private_network=True,
                retries=0,
                overwrite=True,
            ),
            allow_network=True,
        )

    assert destination.read_text(encoding="utf-8") == "trusted old bytes"


def test_unpinned_candidate_requires_explicit_policy(tmp_path: Path) -> None:
    served = tmp_path / "served"
    served.mkdir()
    (served / "fixture.txt").write_text("candidate", encoding="utf-8")

    with local_server(served) as base_url:
        manifest = download_public_artifact(
            source_id="fixture-source",
            release_id="candidate",
            url=f"{base_url}/fixture.txt",
            destination=tmp_path / "candidate.txt",
            expected_sha256=None,
            policy=DownloadPolicy(
                allow_unpinned=True,
                allow_insecure_http=True,
                allow_private_network=True,
                retries=0,
            ),
            allow_network=True,
        )

    assert manifest["pinning"]["status"] == "candidate_unpinned"


def test_download_size_limit_fails_without_committing_file(tmp_path: Path) -> None:
    served = tmp_path / "served"
    served.mkdir()
    (served / "large.bin").write_bytes(b"x" * 128)
    destination = tmp_path / "large.bin"

    with local_server(served) as base_url, pytest.raises(AcquisitionError, match="exceeds limit"):
        download_public_artifact(
            source_id="fixture-source",
            release_id="large",
            url=f"{base_url}/large.bin",
            destination=destination,
            expected_sha256=hashlib.sha256(b"x" * 128).hexdigest(),
            policy=DownloadPolicy(
                allow_insecure_http=True,
                allow_private_network=True,
                max_bytes=64,
                retries=0,
            ),
            allow_network=True,
        )

    assert not destination.exists()
