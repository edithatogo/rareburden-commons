"""Repository-root discovery and safe path resolution."""

from __future__ import annotations

import os
from importlib.resources import files
from pathlib import Path

MARKERS = (
    Path("pyproject.toml"),
    Path("catalog/data_sources.yml"),
    Path("conductor/roadmap.yml"),
)


class PathDiscoveryError(ValueError):
    """Raised when a RareBurden repository root cannot be resolved."""


def is_repository_root(path: Path) -> bool:
    """Return whether *path* contains the minimum RareBurden repository markers."""
    return all((path / marker).is_file() for marker in MARKERS)


def packaged_repository_root() -> Path | None:
    """Return the installed read-only reference repository when available."""
    try:
        candidate = Path(str(files("rareburden").joinpath("resources", "repository")))
    except (ModuleNotFoundError, TypeError):
        return None
    if candidate.is_symlink() or not candidate.is_dir():
        return None
    resolved = candidate.resolve()
    return resolved if is_repository_root(resolved) else None


def discover_repository_root(start: Path | None = None) -> Path:
    """Find the nearest RareBurden repository root.

    ``RAREBURDEN_ROOT`` takes precedence when set. Otherwise the current working
    directory (or *start*) and its parents are searched. The returned path is
    resolved to remove ambiguity from relative paths and symlinks.
    """
    configured = os.environ.get("RAREBURDEN_ROOT")
    candidate = Path(configured).expanduser() if configured else (start or Path.cwd())
    candidate = candidate.resolve()
    search = (candidate, *candidate.parents) if candidate.is_dir() else candidate.parents
    for path in search:
        if is_repository_root(path):
            return path
    raise PathDiscoveryError(
        "Could not locate a RareBurden repository root. Use --root or set RAREBURDEN_ROOT."
    )


def resolve_repository_path(
    root: Path,
    supplied: Path | None,
    default_relative: str,
) -> Path:
    """Resolve a user-supplied path relative to *root*, or use a repository default."""
    value = supplied if supplied is not None else Path(default_relative)
    return value.resolve() if value.is_absolute() else (root / value).resolve()


def resolve_output_path(root: Path, supplied: Path) -> Path:
    """Resolve an output path safely for a checkout or installed reference package.

    Checkout commands retain the historical repository-relative behaviour. When the
    command is using the packaged read-only reference repository, relative outputs are
    written beneath the caller's current working directory instead.
    """
    value = supplied.expanduser()
    if value.is_absolute():
        return value.resolve()
    packaged = packaged_repository_root()
    base = Path.cwd() if packaged is not None and root.resolve() == packaged else root
    return (base / value).resolve()
