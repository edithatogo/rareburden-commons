"""Fail when obvious sensitive or secret-bearing artefacts are present."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DATA_FILES = {
    Path("data/raw/README.md"),
    Path("data/interim/README.md"),
    Path("data/processed/README.md"),
}
SUSPICIOUS_SUFFIXES = {".dcm", ".dicom", ".bam", ".cram", ".vcf", ".bgen", ".pgen"}
SUSPICIOUS_NAMES = {"credentials.json", "secrets.yml", "secrets.yaml", ".env"}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "generic token assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^'\"]{12,}"
    ),
}
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".cff",
    ".ini",
    ".cfg",
}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [Path(item.decode()) for item in result.stdout.split(b"\0") if item]


def main() -> int:
    errors: list[str] = []
    for relative in tracked_files():
        path = ROOT / relative
        if relative.parts and relative.parts[0] == "data" and relative not in ALLOWED_DATA_FILES:
            errors.append(f"unexpected tracked data file: {relative}")
        if path.suffix.lower() in SUSPICIOUS_SUFFIXES or path.name.lower() in SUSPICIOUS_NAMES:
            errors.append(f"suspicious tracked file: {relative}")
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"possible {label} in {relative}")

    if errors:
        print("Repository safety check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Repository safety check passed: {len(tracked_files())} tracked files inspected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
