"""Fail-closed public-source acquisition with immutable provenance."""

from __future__ import annotations

import hashlib
import http.client
import ipaddress
import os
import socket
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Any, BinaryIO
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from rareburden import __version__
from rareburden.provenance import (
    ArtifactRecord,
    ProvenanceError,
    atomic_write_json,
    build_manifest,
    register_local_artifact,
    validate_json_record,
)

_CHUNK_SIZE = 1024 * 1024
_SECRET_QUERY_NAMES = {
    "access_token",
    "api-key",
    "api_key",
    "apikey",
    "auth",
    "key",
    "password",
    "secret",
    "sig",
    "signature",
    "token",
}
_TRANSIENT_HTTP_CODES = {408, 425, 429, 500, 502, 503, 504}


class AcquisitionError(RuntimeError):
    """Raised when acquisition cannot be completed safely."""


class SourceChangedError(AcquisitionError):
    """Raised when acquired bytes do not match the pinned release digest."""


@dataclass(frozen=True)
class DownloadPolicy:
    """Explicit network, integrity and resilience controls for one download."""

    timeout_seconds: float = 30.0
    retries: int = 2
    max_bytes: int = 2 * 1024 * 1024 * 1024
    allow_unpinned: bool = False
    allow_insecure_http: bool = False
    allow_private_network: bool = False
    overwrite: bool = False
    allowed_hosts: frozenset[str] | None = None
    expected_media_types: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise AcquisitionError("timeout_seconds must be positive")
        if not 0 <= self.retries <= 10:
            raise AcquisitionError("retries must be between 0 and 10")
        if self.max_bytes <= 0:
            raise AcquisitionError("max_bytes must be positive")
        if self.allowed_hosts is not None and not self.allowed_hosts:
            raise AcquisitionError("allowed_hosts cannot be an empty set")
        if any("/" not in value for value in self.expected_media_types):
            raise AcquisitionError("expected media types must use type/subtype syntax")


@dataclass(frozen=True)
class AcquisitionRequest:
    """Validated intent to acquire one public release artefact."""

    source_id: str
    release_id: str
    url: str
    destination: Path
    expected_sha256: str | None
    policy: DownloadPolicy = DownloadPolicy()
    repository_root: Path | None = None
    notes: str = ""


@dataclass(frozen=True)
class AcquisitionResult:
    """Successful acquisition output and adjacent provenance manifest."""

    artefact_path: Path
    manifest_path: Path
    manifest: dict[str, Any]


def redact_url(url: str) -> str:
    """Redact likely credentials before a URL enters logs or provenance."""
    parts = urlsplit(url)
    query = [
        (name, "REDACTED" if name.lower() in _SECRET_QUERY_NAMES else value)
        for name, value in parse_qsl(parts.query, keep_blank_values=True)
    ]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _normalise_digest(value: str | None) -> str | None:
    if value is None:
        return None
    digest = value.strip().lower()
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise AcquisitionError("expected_sha256 must be exactly 64 hexadecimal characters")
    return digest


def _public_address(address: str) -> bool:
    value = ipaddress.ip_address(address)
    return not any(
        (
            value.is_private,
            value.is_loopback,
            value.is_link_local,
            value.is_multicast,
            value.is_reserved,
            value.is_unspecified,
        )
    )


def _validate_url(url: str, policy: DownloadPolicy, allowed_hosts: frozenset[str]) -> str:
    parsed = urlsplit(url)
    schemes = {"https"}
    if policy.allow_insecure_http:
        schemes.add("http")
    if parsed.scheme not in schemes:
        raise AcquisitionError(
            f"URL scheme {parsed.scheme!r} is not permitted; HTTPS is required by default"
        )
    if not parsed.hostname:
        raise AcquisitionError("Acquisition URL must include a hostname")
    if parsed.username or parsed.password:
        raise AcquisitionError("Credentials must not be embedded in acquisition URLs")
    hostname = parsed.hostname.lower()
    if hostname not in allowed_hosts:
        raise AcquisitionError(f"Acquisition host is not allow-listed: {hostname}")
    if policy.allow_private_network:
        return hostname
    try:
        addresses = socket.getaddrinfo(
            hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise AcquisitionError(f"Could not resolve acquisition host {hostname}: {exc}") from exc
    if not addresses:
        raise AcquisitionError(f"Acquisition host resolved to no addresses: {hostname}")
    for address in addresses:
        socket_address = address[4]
        if not isinstance(socket_address, tuple) or not socket_address:
            raise AcquisitionError(f"Resolver returned an invalid address for {hostname}")
        resolved = str(socket_address[0])
        if not _public_address(resolved):
            raise AcquisitionError(
                f"Acquisition host resolves to a non-public address ({resolved}); "
                "private-network access requires an explicit trusted-environment override"
            )
    return hostname


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Validate every redirect against the same scheme, host and network policy."""

    def __init__(self, policy: DownloadPolicy, allowed_hosts: frozenset[str]) -> None:
        super().__init__()
        self._policy = policy
        self._allowed_hosts = allowed_hosts

    def redirect_request(
        self,
        request: urllib.request.Request,
        file_pointer: IO[bytes],
        code: int,
        message: str,
        headers: http.client.HTTPMessage,
        new_url: str,
    ) -> urllib.request.Request | None:
        _validate_url(new_url, self._policy, self._allowed_hosts)
        return super().redirect_request(request, file_pointer, code, message, headers, new_url)


def _content_type(headers: Any) -> str:
    try:
        media_type = headers.get_content_type()
    except AttributeError:
        value = headers.get("Content-Type") or headers.get("content-type")
        media_type = str(value).split(";", 1)[0].strip() if value else "application/octet-stream"
    return str(media_type).lower()


def _header(headers: Any, name: str) -> str | None:
    value = headers.get(name)
    return str(value) if value is not None else None


def _stream_response(
    response: BinaryIO, destination: Path, max_bytes: int
) -> tuple[Path, str, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise AcquisitionError(f"Refusing to replace symlink destination: {destination}")
    temporary_path: Path | None = None
    digest = hashlib.sha256()
    size = 0
    try:
        with NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".partial",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            while chunk := response.read(_CHUNK_SIZE):
                size += len(chunk)
                if size > max_bytes:
                    raise AcquisitionError(
                        f"Download exceeds limit of {max_bytes} bytes; no file was committed"
                    )
                digest.update(chunk)
                temporary.write(chunk)
            if size == 0:
                raise AcquisitionError("Refusing an empty source response")
            temporary.flush()
            os.fsync(temporary.fileno())
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    if temporary_path is None:  # pragma: no cover - defensive
        raise AcquisitionError("Download failed before a temporary file was created")
    return temporary_path, digest.hexdigest(), size


def _retry_delay(attempt: int, retry_after: str | None) -> float:
    if retry_after is not None:
        try:
            return min(max(float(retry_after), 0.0), 30.0)
        except ValueError:
            pass
    return min(2.0**attempt, 8.0)


def _download_once(
    *,
    url: str,
    destination: Path,
    policy: DownloadPolicy,
    allowed_hosts: frozenset[str],
) -> tuple[Path, ArtifactRecord, str, str | None, str | None]:
    _validate_url(url, policy, allowed_hosts)
    opener = urllib.request.build_opener(_SafeRedirectHandler(policy, allowed_hosts))
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            "User-Agent": f"rareburden/{__version__} (+https://rareburden.org)",
        },
        method="GET",
    )
    with opener.open(request, timeout=policy.timeout_seconds) as response:
        status = getattr(response, "status", None)
        if status is not None and not 200 <= int(status) < 300:
            raise AcquisitionError(f"Unexpected HTTP status {status}")
        resolved_url = str(response.geturl())
        _validate_url(resolved_url, policy, allowed_hosts)
        content_length = _header(response.headers, "Content-Length")
        if content_length is not None:
            try:
                declared_size = int(content_length)
            except ValueError as exc:
                raise AcquisitionError("Server returned an invalid Content-Length header") from exc
            if declared_size < 0:
                raise AcquisitionError("Server returned a negative Content-Length header")
            if declared_size > policy.max_bytes:
                raise AcquisitionError(
                    f"Declared content length {declared_size} exceeds limit {policy.max_bytes}"
                )
        media_type = _content_type(response.headers)
        permitted_types = {value.lower() for value in policy.expected_media_types}
        if permitted_types and media_type not in permitted_types:
            raise AcquisitionError(
                f"Unexpected media type {media_type!r}; expected one of {sorted(permitted_types)}"
            )
        temporary_path, digest, size = _stream_response(response, destination, policy.max_bytes)
        artifact = ArtifactRecord(
            name=destination.name,
            sha256=digest,
            size_bytes=size,
            media_type=media_type,
        )
        return (
            temporary_path,
            artifact,
            resolved_url,
            _header(response.headers, "ETag"),
            _header(response.headers, "Last-Modified"),
        )


def download_public_artifact(
    *,
    source_id: str,
    release_id: str,
    url: str,
    destination: Path,
    expected_sha256: str | None,
    policy: DownloadPolicy | None = None,
    allow_network: bool = False,
    repository_root: Path | None = None,
    notes: str = "",
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Download one public artefact atomically and return its provenance manifest."""
    effective_policy = policy or DownloadPolicy()
    if not allow_network:
        raise AcquisitionError("Network acquisition is disabled; pass an explicit network opt-in")
    expected = _normalise_digest(expected_sha256)
    if expected is None and not effective_policy.allow_unpinned:
        raise AcquisitionError(
            "An expected SHA-256 digest is required; candidate-unpinned mode must be explicit"
        )
    destination = destination.expanduser()
    if destination.exists() and not effective_policy.overwrite:
        raise AcquisitionError(f"Destination already exists: {destination}")
    if destination.is_symlink():
        raise AcquisitionError(f"Refusing to replace symlink destination: {destination}")

    original_host = urlsplit(url).hostname
    if original_host is None:
        raise AcquisitionError("Acquisition URL must include a hostname")
    allowed_hosts = frozenset(
        value.lower() for value in (effective_policy.allowed_hosts or frozenset({original_host}))
    )
    _validate_url(url, effective_policy, allowed_hosts)

    final_error: BaseException | None = None
    for attempt in range(effective_policy.retries + 1):
        temporary_path: Path | None = None
        try:
            temporary_path, artifact, resolved_url, etag, last_modified = _download_once(
                url=url,
                destination=destination,
                policy=effective_policy,
                allowed_hosts=allowed_hosts,
            )
            if expected is not None and artifact.sha256 != expected:
                raise SourceChangedError(
                    f"Checksum mismatch: expected {expected}, received {artifact.sha256}"
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary_path.replace(destination)
            temporary_path = None
            return build_manifest(
                source_id=source_id,
                release_id=release_id,
                method="direct_download",
                requested_url=redact_url(url),
                resolved_url=redact_url(resolved_url),
                artifact=artifact,
                expected_sha256=expected,
                etag=etag,
                last_modified=last_modified,
                repository_root=repository_root,
                notes=notes,
            )
        except SourceChangedError:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise
        except urllib.error.HTTPError as exc:
            final_error = exc
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            if exc.code not in _TRANSIENT_HTTP_CODES or attempt >= effective_policy.retries:
                break
            sleep(_retry_delay(attempt, exc.headers.get("Retry-After")))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            final_error = exc
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            if attempt >= effective_policy.retries:
                break
            sleep(_retry_delay(attempt, None))
        except AcquisitionError:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise

    raise AcquisitionError(f"Download failed after retries: {final_error}") from final_error


def acquire_http(
    request: AcquisitionRequest,
    *,
    allow_network: bool = False,
    manifest_schema: Path | None = None,
) -> AcquisitionResult:
    """Acquire an artefact and write an adjacent validated acquisition manifest."""
    manifest = download_public_artifact(
        source_id=request.source_id,
        release_id=request.release_id,
        url=request.url,
        destination=request.destination,
        expected_sha256=request.expected_sha256,
        policy=request.policy,
        allow_network=allow_network,
        repository_root=request.repository_root,
        notes=request.notes,
    )
    if manifest_schema is not None:
        validate_json_record(manifest, manifest_schema)
    manifest_path = request.destination.with_name(f"{request.destination.name}.acquisition.json")
    atomic_write_json(manifest_path, manifest)
    return AcquisitionResult(request.destination, manifest_path, manifest)


def register_local_release(
    request: AcquisitionRequest,
    *,
    manifest_schema: Path | None = None,
) -> AcquisitionResult:
    """Register an already-downloaded artefact and write an adjacent manifest."""
    manifest = register_local_artifact(
        source_id=request.source_id,
        release_id=request.release_id,
        source_url=redact_url(request.url),
        artifact_path=request.destination,
        expected_sha256=request.expected_sha256,
        repository_root=request.repository_root,
        notes=request.notes,
    )
    if manifest_schema is not None:
        validate_json_record(manifest, manifest_schema)
    manifest_path = request.destination.with_name(f"{request.destination.name}.acquisition.json")
    atomic_write_json(manifest_path, manifest)
    return AcquisitionResult(request.destination, manifest_path, manifest)


def validate_acquisition_manifest(manifest: dict[str, Any], schema_path: Path) -> None:
    """Validate an acquisition manifest against the canonical contract."""
    try:
        validate_json_record(manifest, schema_path)
    except ProvenanceError as exc:
        raise AcquisitionError(str(exc)) from exc


__all__ = [
    "AcquisitionError",
    "AcquisitionRequest",
    "AcquisitionResult",
    "DownloadPolicy",
    "SourceChangedError",
    "acquire_http",
    "download_public_artifact",
    "redact_url",
    "register_local_release",
    "validate_acquisition_manifest",
]
