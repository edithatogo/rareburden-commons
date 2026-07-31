"""Module entry point for ``python -m rareburden``."""

from rareburden.cli import main

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
