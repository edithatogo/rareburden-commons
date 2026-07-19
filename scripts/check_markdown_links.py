"""Validate repository-local Markdown links without network access."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".venv", "build", "dist", "htmlcov", "venv"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\((?P<target>[^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "doi:", "#")


def _normalise_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    target = unquote(target).split("#", 1)[0].split("?", 1)[0]
    return target


def local_link_errors(root: Path = ROOT) -> list[str]:
    """Return descriptions of broken repository-local Markdown links."""
    errors: list[str] = []
    for document in sorted(root.rglob("*.md")):
        if any(part in IGNORED_PARTS for part in document.relative_to(root).parts):
            continue
        text = document.read_text(encoding="utf-8", errors="replace")
        for match in LINK_RE.finditer(text):
            target = _normalise_target(match.group("target"))
            if not target or target.startswith(EXTERNAL_PREFIXES):
                continue
            if target.startswith("/"):
                resolved = root / target.lstrip("/")
            else:
                resolved = document.parent / target
            if not resolved.resolve().exists():
                relative_document = document.relative_to(root)
                errors.append(f"{relative_document}: missing link target {target!r}")
    return errors


def main() -> int:
    errors = local_link_errors()
    if errors:
        print("Markdown link check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Markdown link check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
