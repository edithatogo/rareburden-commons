#!/usr/bin/env python3
"""Verify and ephemerally package the owner-approved Track 002 candidate.

This command performs read-only publisher retrievals. It never uploads, publishes,
activates, or retains source bytes. Only the caller-selected JSON receipt persists.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, BinaryIO, cast

import yaml

SCOPE = Path("docs/track-002-minimal-public-release-scope-2026-08-20.yml")
EXPECTED_SOURCES = {"orphadata-science-july-2026", "mondo-v2026-08-04"}
ALLOWED_FINAL_HOSTS = {
    "orphadata-science-july-2026": {"www.orphadata.com"},
    "mondo-v2026-08-04": {
        "github.com",
        "release-assets.githubusercontent.com",
        "objects.githubusercontent.com",
    },
}
TERMS = (
    {
        "id": "orphadata_epidemiology",
        "url": "https://sciences.orphadata.com/epidemiology/",
        "required": ("en_product9_prev.xml", "CC BY 4.0", "July 2026"),
    },
    {
        "id": "orphadata_alignments",
        "url": "https://sciences.orphadata.com/alignments/",
        "required": ("en_product1.xml", "CC BY 4.0", "July 2026"),
    },
    {
        "id": "orphadata_legal_notice",
        "url": "https://sciences.orphadata.com/legal-notice/",
        "required": ("CC BY 4.0", "credit", "changes"),
    },
    {
        "id": "mondo_download",
        "url": "https://mondo.monarchinitiative.org/pages/download/",
        "required": ("mondo.owl", "mondo-rare.owl", "mondo.json", "CC BY 4.0"),
    },
    {
        "id": "mondo_release",
        "url": "https://github.com/monarch-initiative/mondo/releases/tag/v2026-08-04",
        "required": ("v2026-08-04",),
    },
    {
        "id": "mondo_release_api_digests",
        "url": "https://api.github.com/repos/monarch-initiative/mondo/releases/tags/v2026-08-04",
        "required": (
            "87361d63636436611e27d408be53606f8e831a2fd6ab70a4969ec54d19cb66d3",
            "7cf8f1df31185555a21f5ffaf36663ca420671a9bc234fc737eb9bfa977ecd60",
            "afb2e699abf77082253ef51cca5f8531c8e4023ea0acc32ff3709818d0788a88",
        ),
    },
)
TERMS_HOSTS = {
    "sciences.orphadata.com",
    "mondo.monarchinitiative.org",
    "github.com",
    "api.github.com",
}
MAX_TERMS_BYTES = 5 * 1024 * 1024
MONDO_RANGE_BYTES = 16 * 1024 * 1024
USER_AGENT = "rareburden-track-002-candidate-verifier/1"


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


class HashingSink:
    """A write-only counter and SHA-256 sink for a streamed tar archive."""

    def __init__(self) -> None:
        self.digest = hashlib.sha256()
        self.size = 0

    def write(self, data: bytes) -> int:
        self.digest.update(data)
        self.size += len(data)
        return len(data)

    def flush(self) -> None:
        return None


def _safe_scope(scope: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    authority = scope.get("authority", {})
    if authority.get("publication_authorized") is not False:
        raise ValueError("scope must not authorize publication")
    if authority.get("external_mutation_authorized") is not False:
        raise ValueError("scope must not authorize external mutation")
    if any(scope.get("claims", {}).values()):
        raise ValueError("candidate claims must remain false")
    sources = scope.get("candidate", {}).get("sources", [])
    if {source.get("source_id") for source in sources} != EXPECTED_SOURCES:
        raise ValueError("candidate source allowlist changed")
    artifacts: list[tuple[str, dict[str, Any]]] = []
    for source in sources:
        source_id = str(source["source_id"])
        for artifact in source.get("artifacts", []):
            name = str(artifact.get("name", ""))
            public_path = str(artifact.get("public_path", ""))
            parsed = urllib.parse.urlsplit(str(artifact.get("source_url", "")))
            if Path(name).name != name or not name or Path(public_path).is_absolute():
                raise ValueError("unsafe candidate artifact path")
            if ".." in Path(public_path).parts or Path(public_path).name != name:
                raise ValueError("unsafe candidate public path")
            if parsed.scheme != "https" or parsed.hostname not in {
                "www.orphadata.com",
                "github.com",
            }:
                raise ValueError("candidate source URL is outside the publisher allowlist")
            if parsed.username or parsed.password or parsed.query or parsed.fragment:
                raise ValueError("candidate source URL must be credential-free and query-free")
            if int(artifact.get("bytes", 0)) <= 0 or not _is_sha256(artifact.get("sha256")):
                raise ValueError("candidate artifact lacks an exact size and SHA-256")
            artifacts.append((source_id, artifact))
    if len(artifacts) != 5 or len({str(item[1]["public_path"]) for item in artifacts}) != 5:
        raise ValueError("candidate must contain exactly five unique artifacts")
    return artifacts


def _open(url: str, *, timeout: float = 240.0, headers: dict[str, str] | None = None) -> Any:
    request_headers = {"User-Agent": USER_AGENT}
    request_headers.update(headers or {})
    request = urllib.request.Request(url, headers=request_headers)
    return urllib.request.urlopen(request, timeout=timeout)


def _read_bounded(response: BinaryIO, *, max_bytes: int) -> bytes:
    chunks = bytearray()
    while chunk := response.read(min(1024 * 1024, max_bytes + 1 - len(chunks))):
        chunks.extend(chunk)
        if len(chunks) > max_bytes:
            raise ValueError("response exceeded byte budget")
    return bytes(chunks)


def observe_terms() -> list[dict[str, Any]]:
    observations = []
    for item in TERMS:
        failures = []
        for attempt in range(1, 3):
            try:
                observation = _observe_term_once(item, attempt=attempt)
                observations.append(observation)
                break
            except (OSError, ValueError) as error:
                failures.append(f"attempt {attempt}: {error}")
                if attempt < 2:
                    time.sleep(2)
        else:
            raise ValueError(f"terms observation failed for {item['id']}: {failures}")
    return observations


def _observe_term_once(item: dict[str, Any], *, attempt: int) -> dict[str, Any]:
    with _open(str(item["url"]), timeout=90.0) as response:
        final_url = response.geturl()
        final_host = urllib.parse.urlsplit(final_url).hostname
        if final_host not in TERMS_HOSTS:
            raise ValueError(f"unexpected terms redirect host for {item['id']}")
        body = _read_bounded(response, max_bytes=MAX_TERMS_BYTES)
        text = body.decode("utf-8", errors="replace")
        missing = [token for token in item["required"] if token.casefold() not in text.casefold()]
        if missing:
            raise ValueError(f"terms markers missing for {item['id']}: {missing}")
        return {
            "id": item["id"],
            "requested_url": item["url"],
            "final_url": final_url,
            "http_status": int(response.status),
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "required_markers_present": list(item["required"]),
            "verification_attempt": attempt,
        }


def _download_artifact(
    source_id: str, artifact: dict[str, Any], destination: Path
) -> dict[str, Any]:
    if source_id == "mondo-v2026-08-04":
        return _download_ranged_artifact(source_id, artifact, destination)
    failures = []
    for attempt in range(1, 3):
        destination.unlink(missing_ok=True)
        try:
            return _download_artifact_once(source_id, artifact, destination, attempt=attempt)
        except (OSError, ValueError) as error:
            failures.append(f"attempt {attempt}: {error}")
            destination.unlink(missing_ok=True)
            if attempt < 2:
                time.sleep(2)
    raise ValueError(f"artifact verification failed for {artifact['name']}: {failures}")


def _validate_content_range(value: str | None, *, start: int, end: int, total: int) -> None:
    expected = f"bytes {start}-{end}/{total}"
    if value != expected:
        raise ValueError(f"unexpected Content-Range: expected {expected!r}, observed {value!r}")


def _download_ranged_artifact(
    source_id: str, artifact: dict[str, Any], destination: Path
) -> dict[str, Any]:
    expected_size = int(artifact["bytes"])
    digest = hashlib.sha256()
    destination.parent.mkdir(parents=True, exist_ok=True)
    maximum_attempt = 1
    final_host = ""
    content_type = None
    last_modified = None
    with destination.open("wb") as output:
        for start in range(0, expected_size, MONDO_RANGE_BYTES):
            end = min(start + MONDO_RANGE_BYTES, expected_size) - 1
            expected_chunk_size = end - start + 1
            failures = []
            for attempt in range(1, 4):
                try:
                    with _open(
                        str(artifact["source_url"]),
                        headers={"Range": f"bytes={start}-{end}"},
                    ) as response:
                        final_host = urllib.parse.urlsplit(response.geturl()).hostname or ""
                        if final_host not in ALLOWED_FINAL_HOSTS[source_id]:
                            raise ValueError(
                                f"unexpected artifact redirect host for {artifact['name']}"
                            )
                        if int(response.status) != 206:
                            raise ValueError(
                                f"range request returned HTTP {response.status} "
                                f"for {artifact['name']}"
                            )
                        _validate_content_range(
                            response.headers.get("Content-Range"),
                            start=start,
                            end=end,
                            total=expected_size,
                        )
                        chunk = _read_bounded(response, max_bytes=expected_chunk_size)
                        if len(chunk) != expected_chunk_size:
                            raise ValueError(
                                f"short range for {artifact['name']}: expected "
                                f"{expected_chunk_size}, observed {len(chunk)}"
                            )
                        content_type = response.headers.get("Content-Type")
                        last_modified = response.headers.get("Last-Modified")
                    output.write(chunk)
                    digest.update(chunk)
                    maximum_attempt = max(maximum_attempt, attempt)
                    break
                except (OSError, ValueError) as error:
                    failures.append(f"attempt {attempt}: {error}")
                    if attempt < 3:
                        time.sleep(2)
            else:
                raise ValueError(f"range {start}-{end} failed for {artifact['name']}: {failures}")
            if end + 1 < expected_size:
                time.sleep(0.1)
    actual_size = destination.stat().st_size
    actual_sha256 = digest.hexdigest()
    if actual_size != expected_size or actual_sha256 != artifact["sha256"]:
        raise ValueError(
            f"exact ranged size or SHA-256 drift for {artifact['name']}: "
            f"observed bytes={actual_size}, sha256={actual_sha256}"
        )
    return {
        "source_id": source_id,
        "name": artifact["name"],
        "requested_url": artifact["source_url"],
        "final_host": final_host,
        "http_status": 206,
        "content_type": content_type,
        "last_modified": last_modified,
        "public_path": artifact["public_path"],
        "bytes": actual_size,
        "sha256": actual_sha256,
        "verification_attempt": maximum_attempt,
        "transport": {
            "method": "validated_https_byte_ranges",
            "range_bytes": MONDO_RANGE_BYTES,
        },
        "disposition": "exact_unmodified_ephemeral_candidate_byte",
    }


def _download_artifact_once(
    source_id: str, artifact: dict[str, Any], destination: Path, *, attempt: int
) -> dict[str, Any]:
    expected_size = int(artifact["bytes"])
    digest = hashlib.sha256()
    size = 0
    with _open(str(artifact["source_url"])) as response:
        final_url = response.geturl()
        final_host = urllib.parse.urlsplit(final_url).hostname
        if final_host not in ALLOWED_FINAL_HOSTS[source_id]:
            raise ValueError(f"unexpected artifact redirect host for {artifact['name']}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                size += len(chunk)
                if size > expected_size:
                    raise ValueError(f"artifact exceeded exact size for {artifact['name']}")
                digest.update(chunk)
                output.write(chunk)
        status = int(response.status)
        last_modified = response.headers.get("Last-Modified")
        content_type = response.headers.get("Content-Type")
    actual_sha256 = digest.hexdigest()
    if size != expected_size or actual_sha256 != artifact["sha256"]:
        raise ValueError(
            f"exact size or SHA-256 drift for {artifact['name']}: "
            f"observed bytes={size}, sha256={actual_sha256}"
        )
    return {
        "source_id": source_id,
        "name": artifact["name"],
        "requested_url": artifact["source_url"],
        "final_host": final_host,
        "http_status": status,
        "content_type": content_type,
        "last_modified": last_modified,
        "public_path": artifact["public_path"],
        "bytes": size,
        "sha256": actual_sha256,
        "verification_attempt": attempt,
        "disposition": "exact_unmodified_ephemeral_candidate_byte",
    }


def _candidate_notice() -> bytes:
    return (
        b"Track 002 minimal public candidate\n\n"
        b"Orphadata Science / Orphanet, July 2026 release. CC BY 4.0. "
        b"Files are unchanged; attribution and change notice are preserved. "
        b"No endorsement is implied.\n\n"
        b"Mondo Disease Ontology, Monarch Initiative, release v2026-08-04. "
        b"CC BY 4.0. Files are unchanged and exact-release pinned. "
        b"No endorsement or clinical validation is implied.\n\n"
        b"This bounded source snapshot does not claim comprehensive coverage, "
        b"systematic review, global representativeness, confirmed novelty, "
        b"independent review, community authority, clinical validation, partnership, "
        b"access, or external approval.\n"
    )


def _tar_info(name: str, size: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.size = size
    info.mtime = 0
    info.mode = 0o644
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    return info


def deterministic_package_digest(root: Path, manifest: bytes, notice: bytes) -> tuple[int, str]:
    sink = HashingSink()
    with tarfile.open(fileobj=cast(Any, sink), mode="w|", format=tarfile.PAX_FORMAT) as archive:
        for name, data in (("MANIFEST.json", manifest), ("NOTICE.md", notice)):
            archive.addfile(_tar_info(name, len(data)), io.BytesIO(data))
        files = sorted(path for path in root.rglob("*") if path.is_file())
        for path in files:
            arcname = path.relative_to(root).as_posix()
            with path.open("rb") as source:
                archive.addfile(_tar_info(arcname, path.stat().st_size), source)
    return sink.size, sink.digest.hexdigest()


def verify(scope_path: Path) -> dict[str, Any]:
    scope_bytes = scope_path.read_bytes()
    scope = yaml.safe_load(scope_bytes)
    artifacts = _safe_scope(scope)
    terms = observe_terms()
    temporary = Path(tempfile.mkdtemp(prefix="rareburden-track002-candidate-"))
    try:
        verified = []
        for source_id, artifact in artifacts:
            destination = temporary / str(artifact["public_path"])
            verified.append(_download_artifact(source_id, artifact, destination))
        manifest = json.dumps(
            {
                "schema_version": "1.0",
                "scope_sha256": hashlib.sha256(scope_bytes).hexdigest(),
                "artifacts": verified,
                "activation": "disabled",
                "publication_authorized": False,
            },
            indent=2,
            sort_keys=True,
        ).encode()
        notice = _candidate_notice()
        package_bytes, package_sha256 = deterministic_package_digest(temporary, manifest, notice)
    finally:
        shutil.rmtree(temporary, ignore_errors=False)
    if temporary.exists():
        raise RuntimeError("ephemeral candidate cleanup failed")
    return {
        "schema_version": "1.0",
        "decision_id": scope["decision_id"],
        "observed_at": datetime.now(UTC).isoformat(),
        "status": "verified_ephemeral_candidate_not_published",
        "scope_path": scope_path.as_posix(),
        "scope_sha256": hashlib.sha256(scope_bytes).hexdigest(),
        "terms_observations": terms,
        "artifacts": verified,
        "package": {
            "format": "deterministic_pax_tar_stream",
            "bytes": package_bytes,
            "sha256": package_sha256,
            "retained": False,
        },
        "cleanup": {"source_bytes_retained": False, "temporary_directory_removed": True},
        "authority": {
            "publication_authorized": False,
            "external_mutation_performed": False,
            "credential_used": False,
            "private_capture_performed": False,
        },
        "claims": scope["claims"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", type=Path, default=SCOPE)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = verify(args.scope)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    try:
        with args.receipt.open("x", encoding="utf-8", errors="strict") as stream:
            stream.write(rendered)
    except FileExistsError as exc:
        raise ValueError(f"refusing to overwrite receipt: {args.receipt}") from exc
    print(json.dumps({"status": receipt["status"], "receipt": str(args.receipt)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
