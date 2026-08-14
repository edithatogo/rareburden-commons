from __future__ import annotations

import re
from pathlib import Path

PROBE = Path(__file__).parents[1] / "docs/track-002-live-reachability-probe-2026-08-03.md"


def test_live_probe_records_four_canonical_sha256_values() -> None:
    text = PROBE.read_text(encoding="utf-8")
    hashes = re.findall(r"`([0-9a-f]{64})`", text)
    assert len(hashes) == 4
    assert len(set(hashes)) == 4
