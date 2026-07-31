"""Check deterministic synthetic node output without network or filesystem input."""

from __future__ import annotations

import json

from rareburden.node import build_synthetic_cohort, run_offline_node


def _run() -> dict[str, object]:
    return run_offline_node(
        build_synthetic_cohort(),
        execution_id="synthetic-reproducibility",
        coordinator_version="0.1.0",
        node_version="0.1.1",
        analysis_id="synthetic-analysis",
        policy_id="synthetic-policy",
        input_fingerprint="sha256:synthetic-input",
    )


first = json.dumps(_run(), sort_keys=True, separators=(",", ":"))
second = json.dumps(_run(), sort_keys=True, separators=(",", ":"))
if first != second:
    raise SystemExit("synthetic node output is not deterministic")
print("Synthetic node reproducibility passed")
