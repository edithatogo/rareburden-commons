#!/usr/bin/env python3
"""Build deterministic wheel and source distributions without network or isolation."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import os
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

import setuptools.build_meta as backend


class DistributionBuildError(RuntimeError):
    """Raised when a distribution build is incomplete or non-reproducible."""


def _safe_archive_name(name: str) -> str:
    pure = PurePosixPath(name)
    if (
        not name
        or pure.is_absolute()
        or ".." in pure.parts
        or "\\" in name
        or any(ord(character) < 32 for character in name)
    ):
        raise DistributionBuildError(f"Unsafe source-distribution member: {name!r}")
    return pure.as_posix()


def _canonicalise_sdist(path: Path, *, source_date_epoch: int) -> None:
    """Rewrite a generated sdist with stable tar and gzip metadata."""
    records: list[tuple[str, bool, int, bytes]] = []
    try:
        with tarfile.open(path, "r:*") as archive:
            for member in archive.getmembers():
                name = _safe_archive_name(member.name)
                if member.issym() or member.islnk() or member.isdev():
                    raise DistributionBuildError(
                        f"Unsafe source-distribution member type: {name}"
                    )
                if member.isdir():
                    records.append((name.rstrip("/") + "/", True, 0o755, b""))
                    continue
                if not member.isfile():
                    continue
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise DistributionBuildError(
                        f"Cannot read source-distribution member: {name}"
                    )
                data = extracted.read()
                mode = 0o755 if member.mode & 0o111 else 0o644
                records.append((name, False, mode, data))
    except (OSError, tarfile.TarError) as exc:
        raise DistributionBuildError(f"Cannot canonicalise source distribution: {exc}") from exc

    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.GNU_FORMAT) as canonical:
        for name, is_directory, mode, data in sorted(records, key=lambda item: item[0]):
            info = tarfile.TarInfo(name=name)
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mtime = source_date_epoch
            info.mode = mode
            if is_directory:
                info.type = tarfile.DIRTYPE
                info.size = 0
                canonical.addfile(info)
            else:
                info.type = tarfile.REGTYPE
                info.size = len(data)
                canonical.addfile(info, io.BytesIO(data))

    temporary = path.with_name(f".{path.name}.canonical")
    try:
        with temporary.open("wb") as raw:
            with gzip.GzipFile(
                filename="", mode="wb", fileobj=raw, mtime=source_date_epoch, compresslevel=9
            ) as compressed:
                compressed.write(buffer.getvalue())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _clean_generated(root: Path) -> None:
    for path in (root / "build", root / "src" / "rareburden.egg-info"):
        if path.exists():
            if path.is_symlink():
                raise DistributionBuildError(f"Refusing unsafe generated path: {path}")
            shutil.rmtree(path)


def _build_once(root: Path, output: Path) -> dict[str, bytes]:
    output.mkdir(parents=True, exist_ok=True)
    previous = Path.cwd()
    try:
        os.chdir(root)
        _clean_generated(root)
        wheel_name = backend.build_wheel(str(output), config_settings={})
        sdist_name = backend.build_sdist(str(output), config_settings={})
        _canonicalise_sdist(output / sdist_name, source_date_epoch=int(os.environ["SOURCE_DATE_EPOCH"]))
    except Exception as exc:
        raise DistributionBuildError(f"Distribution build failed: {exc}") from exc
    finally:
        os.chdir(previous)
        _clean_generated(root)
    names = {wheel_name, sdist_name}
    if len(names) != 2:
        raise DistributionBuildError("Build backend did not return one wheel and one source distribution")
    records: dict[str, bytes] = {}
    for name in sorted(names):
        path = output / name
        if path.is_symlink() or not path.is_file():
            raise DistributionBuildError(f"Build backend did not create a safe distribution: {path}")
        records[name] = path.read_bytes()
    return records


def build_reproducible_distributions(
    root: Path,
    output: Path,
    *,
    source_date_epoch: int,
) -> dict[str, str]:
    """Build twice, require byte identity, then publish one exact pair."""
    repository_root = root.expanduser().resolve()
    destination = output.expanduser().resolve()
    if repository_root.is_symlink() or not repository_root.is_dir():
        raise DistributionBuildError(f"Repository root is missing or unsafe: {root}")
    os.environ["SOURCE_DATE_EPOCH"] = str(source_date_epoch)
    with (
        tempfile.TemporaryDirectory(prefix="rareburden-build-a-") as first_raw,
        tempfile.TemporaryDirectory(prefix="rareburden-build-b-") as second_raw,
    ):
        first = _build_once(repository_root, Path(first_raw))
        second = _build_once(repository_root, Path(second_raw))
        if first.keys() != second.keys():
            raise DistributionBuildError("Repeated builds produced different distribution names")
        changed = sorted(name for name in first if first[name] != second[name])
        if changed:
            raise DistributionBuildError("Repeated builds are not byte-for-byte reproducible: " + ", ".join(changed))
        if destination.exists():
            if destination.is_symlink() or not destination.is_dir():
                raise DistributionBuildError(f"Distribution destination is unsafe: {destination}")
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        digests: dict[str, str] = {}
        for name, data in first.items():
            (destination / name).write_bytes(data)
            digests[name] = hashlib.sha256(data).hexdigest()
        return digests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--source-date-epoch", type=int, default=1760000000)
    args = parser.parse_args()
    try:
        digests = build_reproducible_distributions(
            args.root,
            args.output,
            source_date_epoch=args.source_date_epoch,
        )
    except DistributionBuildError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for name, digest in sorted(digests.items()):
        print(f"{digest}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
