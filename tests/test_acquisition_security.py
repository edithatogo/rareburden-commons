from __future__ import annotations

import hashlib
import io
import socket
import urllib.error
from pathlib import Path
from typing import Any

import pytest

import rareburden.acquisition.core as core
from rareburden.acquisition import (
    AcquisitionError,
    AcquisitionRequest,
    DownloadPolicy,
    SourceChangedError,
    acquire_http,
    download_public_artifact,
    redact_url,
    register_local_release,
    validate_acquisition_manifest,
)
from rareburden.provenance import ArtifactRecord


class _FakeResponse(io.BytesIO):
    def __init__(
        self,
        payload: bytes,
        *,
        url: str = "https://example.org/data.csv",
        status: int = 200,
        headers: Any | None = None,
    ) -> None:
        super().__init__(payload)
        self._url = url
        self.status = status
        self.headers = headers if headers is not None else {"Content-Type": "text/csv"}

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def geturl(self) -> str:
        return self._url


class _FakeOpener:
    def __init__(self, response: _FakeResponse) -> None:
        self.response = response

    def open(self, _request: object, *, timeout: float) -> _FakeResponse:
        assert timeout > 0
        return self.response


@pytest.mark.parametrize(
    "kwargs",
    [
        {"timeout_seconds": 0},
        {"retries": -1},
        {"retries": 11},
        {"max_bytes": 0},
        {"allowed_hosts": frozenset()},
        {"expected_media_types": ("csv",)},
    ],
)
def test_download_policy_rejects_unsafe_values(kwargs: dict[str, Any]) -> None:
    with pytest.raises(AcquisitionError):
        DownloadPolicy(**kwargs)


def test_redact_url_preserves_nonsecret_fields_and_redacts_credentials() -> None:
    value = redact_url("https://example.org/data?token=secret&year=2023&API_KEY=hidden&blank=#part")
    assert "secret" not in value
    assert "hidden" not in value
    assert "token=REDACTED" in value
    assert "API_KEY=REDACTED" in value
    assert "year=2023" in value
    assert "blank=" in value
    assert value.endswith("#part")


@pytest.mark.parametrize("digest", ["", "0" * 63, "g" * 64, "0" * 65])
def test_download_rejects_invalid_expected_digest(tmp_path: Path, digest: str) -> None:
    with pytest.raises(AcquisitionError, match="64 hexadecimal"):
        download_public_artifact(
            source_id="source",
            release_id="release",
            url="https://example.org/data",
            destination=tmp_path / "data",
            expected_sha256=digest,
            allow_network=True,
            policy=DownloadPolicy(allow_private_network=True),
        )


def test_url_policy_rejects_scheme_credentials_and_unlisted_host() -> None:
    policy = DownloadPolicy(allow_private_network=True)
    with pytest.raises(AcquisitionError, match="scheme"):
        core._validate_url("ftp://example.org/data", policy, frozenset({"example.org"}))
    with pytest.raises(AcquisitionError, match="hostname"):
        core._validate_url("https:///data", policy, frozenset({"example.org"}))
    with pytest.raises(AcquisitionError, match="Credentials"):
        core._validate_url(
            "https://user:password@example.org/data", policy, frozenset({"example.org"})
        )
    with pytest.raises(AcquisitionError, match="allow-listed"):
        core._validate_url("https://other.org/data", policy, frozenset({"example.org"}))


def test_url_policy_validates_dns_and_public_addresses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy = DownloadPolicy()
    allowed = frozenset({"example.org"})

    def fail_resolution(*_args: object, **_kwargs: object) -> Any:
        raise socket.gaierror("fixture failure")

    monkeypatch.setattr(core.socket, "getaddrinfo", fail_resolution)
    with pytest.raises(AcquisitionError, match="Could not resolve"):
        core._validate_url("https://example.org/data", policy, allowed)

    monkeypatch.setattr(core.socket, "getaddrinfo", lambda *_args, **_kwargs: [])
    with pytest.raises(AcquisitionError, match="no addresses"):
        core._validate_url("https://example.org/data", policy, allowed)

    malformed = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", None)]
    monkeypatch.setattr(core.socket, "getaddrinfo", lambda *_args, **_kwargs: malformed)
    with pytest.raises(AcquisitionError, match="invalid address"):
        core._validate_url("https://example.org/data", policy, allowed)

    private = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]
    monkeypatch.setattr(core.socket, "getaddrinfo", lambda *_args, **_kwargs: private)
    with pytest.raises(AcquisitionError, match="non-public address"):
        core._validate_url("https://example.org/data", policy, allowed)

    public = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
    monkeypatch.setattr(core.socket, "getaddrinfo", lambda *_args, **_kwargs: public)
    assert core._validate_url("https://example.org/data", policy, allowed) == "example.org"


def test_content_type_and_retry_delay_fallbacks() -> None:
    assert core._content_type({"content-type": "Text/CSV; charset=utf-8"}) == "text/csv"
    assert core._content_type({}) == "application/octet-stream"
    assert core._retry_delay(0, "5") == 5
    assert core._retry_delay(0, "-2") == 0
    assert core._retry_delay(0, "99") == 30
    assert core._retry_delay(2, "not-a-number") == 4
    assert core._retry_delay(10, None) == 8


def test_stream_response_rejects_symlinks_empty_and_oversize(tmp_path: Path) -> None:
    destination = tmp_path / "data.bin"
    target = tmp_path / "target.bin"
    target.write_bytes(b"trusted")
    destination.symlink_to(target)
    with pytest.raises(AcquisitionError, match="symlink"):
        core._stream_response(io.BytesIO(b"data"), destination, 100)

    destination.unlink()
    with pytest.raises(AcquisitionError, match="empty"):
        core._stream_response(io.BytesIO(b""), destination, 100)
    assert not list(tmp_path.glob(".*.partial"))

    with pytest.raises(AcquisitionError, match="exceeds limit"):
        core._stream_response(io.BytesIO(b"12345"), destination, 4)
    assert not list(tmp_path.glob(".*.partial"))

    temporary, digest, size = core._stream_response(io.BytesIO(b"abc"), destination, 3)
    try:
        assert digest == hashlib.sha256(b"abc").hexdigest()
        assert size == 3
        assert temporary.read_bytes() == b"abc"
    finally:
        temporary.unlink()


@pytest.mark.parametrize(
    ("status", "headers", "message"),
    [
        (500, {"Content-Type": "text/csv"}, "Unexpected HTTP status"),
        (200, {"Content-Type": "text/csv", "Content-Length": "bad"}, "invalid Content-Length"),
        (200, {"Content-Type": "text/csv", "Content-Length": "-1"}, "negative Content-Length"),
        (200, {"Content-Type": "text/csv", "Content-Length": "101"}, "exceeds limit"),
        (200, {"Content-Type": "application/json"}, "Unexpected media type"),
    ],
)
def test_download_once_rejects_bad_responses(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: int,
    headers: dict[str, str],
    message: str,
) -> None:
    response = _FakeResponse(b"data", status=status, headers=headers)
    monkeypatch.setattr(core.urllib.request, "build_opener", lambda *_args: _FakeOpener(response))
    policy = DownloadPolicy(
        allow_private_network=True,
        max_bytes=100,
        expected_media_types=("text/csv",),
    )
    with pytest.raises(AcquisitionError, match=message):
        core._download_once(
            url="https://example.org/data.csv",
            destination=tmp_path / "data.csv",
            policy=policy,
            allowed_hosts=frozenset({"example.org"}),
        )


def test_download_once_returns_headers_and_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    headers = {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Length": "4",
        "ETag": '"fixture"',
        "Last-Modified": "Sun, 19 Jul 2026 00:00:00 GMT",
    }
    response = _FakeResponse(b"data", headers=headers)
    monkeypatch.setattr(core.urllib.request, "build_opener", lambda *_args: _FakeOpener(response))
    result = core._download_once(
        url="https://example.org/data.csv",
        destination=tmp_path / "data.csv",
        policy=DownloadPolicy(
            allow_private_network=True,
            max_bytes=100,
            expected_media_types=("text/csv",),
        ),
        allowed_hosts=frozenset({"example.org"}),
    )
    temporary, artifact, resolved_url, etag, modified = result
    try:
        assert artifact.size_bytes == 4
        assert artifact.media_type == "text/csv"
        assert resolved_url == "https://example.org/data.csv"
        assert etag == '"fixture"'
        assert modified == "Sun, 19 Jul 2026 00:00:00 GMT"
    finally:
        temporary.unlink()


def _artifact_result(
    tmp_path: Path, payload: bytes
) -> tuple[Path, ArtifactRecord, str, None, None]:
    temporary = tmp_path / "download.partial"
    temporary.write_bytes(payload)
    return (
        temporary,
        ArtifactRecord(
            name="data.bin",
            sha256=hashlib.sha256(payload).hexdigest(),
            size_bytes=len(payload),
            media_type="application/octet-stream",
        ),
        "https://example.org/data.bin",
        None,
        None,
    )


def test_download_retries_transient_http_then_succeeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def download_once(**_kwargs: object) -> Any:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise urllib.error.HTTPError(
                "https://example.org/data.bin",
                503,
                "unavailable",
                {"Retry-After": "0"},
                None,
            )
        return _artifact_result(tmp_path, b"payload")

    monkeypatch.setattr(core, "_download_once", download_once)
    sleeps: list[float] = []
    destination = tmp_path / "data.bin"
    manifest = download_public_artifact(
        source_id="source",
        release_id="release",
        url="https://example.org/data.bin?token=secret",
        destination=destination,
        expected_sha256=hashlib.sha256(b"payload").hexdigest(),
        policy=DownloadPolicy(allow_private_network=True, retries=1),
        allow_network=True,
        sleep=sleeps.append,
    )
    assert calls == 2
    assert sleeps == [0]
    assert destination.read_bytes() == b"payload"
    assert "secret" not in manifest["requested_url"]


def test_download_retries_url_errors_and_reports_final_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(**_kwargs: object) -> Any:
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(core, "_download_once", fail)
    sleeps: list[float] = []
    with pytest.raises(AcquisitionError, match="after retries"):
        download_public_artifact(
            source_id="source",
            release_id="release",
            url="https://example.org/data.bin",
            destination=tmp_path / "data.bin",
            expected_sha256="0" * 64,
            policy=DownloadPolicy(allow_private_network=True, retries=1),
            allow_network=True,
            sleep=sleeps.append,
        )
    assert sleeps == [1]


def test_download_does_not_retry_nontransient_http(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def fail(**_kwargs: object) -> Any:
        nonlocal calls
        calls += 1
        raise urllib.error.HTTPError("https://example.org/data.bin", 404, "not found", {}, None)

    monkeypatch.setattr(core, "_download_once", fail)
    with pytest.raises(AcquisitionError, match="after retries"):
        download_public_artifact(
            source_id="source",
            release_id="release",
            url="https://example.org/data.bin",
            destination=tmp_path / "data.bin",
            expected_sha256="0" * 64,
            policy=DownloadPolicy(allow_private_network=True, retries=3),
            allow_network=True,
            sleep=lambda _delay: pytest.fail("non-transient HTTP errors must not retry"),
        )
    assert calls == 1


def test_checksum_mismatch_removes_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        core, "_download_once", lambda **_kwargs: _artifact_result(tmp_path, b"bad")
    )
    with pytest.raises(SourceChangedError, match="Checksum mismatch"):
        download_public_artifact(
            source_id="source",
            release_id="release",
            url="https://example.org/data.bin",
            destination=tmp_path / "data.bin",
            expected_sha256=hashlib.sha256(b"expected").hexdigest(),
            policy=DownloadPolicy(allow_private_network=True),
            allow_network=True,
        )
    assert not (tmp_path / "download.partial").exists()


def test_download_rejects_existing_symlink_and_missing_host(tmp_path: Path) -> None:
    destination = tmp_path / "data.bin"
    destination.write_bytes(b"existing")
    with pytest.raises(AcquisitionError, match="already exists"):
        download_public_artifact(
            source_id="source",
            release_id="release",
            url="https://example.org/data.bin",
            destination=destination,
            expected_sha256="0" * 64,
            policy=DownloadPolicy(allow_private_network=True),
            allow_network=True,
        )

    destination.unlink()
    target = tmp_path / "target.bin"
    target.write_bytes(b"target")
    destination.symlink_to(target)
    with pytest.raises(AcquisitionError, match="symlink"):
        download_public_artifact(
            source_id="source",
            release_id="release",
            url="https://example.org/data.bin",
            destination=destination,
            expected_sha256="0" * 64,
            policy=DownloadPolicy(allow_private_network=True, overwrite=True),
            allow_network=True,
        )

    with pytest.raises(AcquisitionError, match="hostname"):
        download_public_artifact(
            source_id="source",
            release_id="release",
            url="https:///data.bin",
            destination=tmp_path / "other.bin",
            expected_sha256="0" * 64,
            policy=DownloadPolicy(allow_private_network=True),
            allow_network=True,
        )


def test_acquisition_wrappers_write_and_validate_manifests(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact = tmp_path / "local.csv"
    artifact.write_text("a,b\n1,2\n", encoding="utf-8")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    request = AcquisitionRequest(
        source_id="local-source",
        release_id="r1",
        url="https://example.org/local.csv?api_key=secret",
        destination=artifact,
        expected_sha256=digest,
    )
    registered = register_local_release(
        request,
        manifest_schema=Path("schemas/acquisition-manifest.schema.json"),
    )
    assert registered.manifest_path.is_file()
    assert "secret" not in registered.manifest["requested_url"]
    validate_acquisition_manifest(
        registered.manifest, Path("schemas/acquisition-manifest.schema.json")
    )

    destination = tmp_path / "downloaded.csv"
    manifest = dict(registered.manifest)
    monkeypatch.setattr(core, "download_public_artifact", lambda **_kwargs: manifest)
    acquired = acquire_http(
        AcquisitionRequest(
            source_id="local-source",
            release_id="r1",
            url="https://example.org/downloaded.csv",
            destination=destination,
            expected_sha256=digest,
        )
    )
    assert acquired.manifest_path.is_file()

    with pytest.raises(AcquisitionError):
        validate_acquisition_manifest(
            {"schema_version": "invalid"},
            Path("schemas/acquisition-manifest.schema.json"),
        )
