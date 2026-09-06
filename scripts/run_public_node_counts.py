"""Offline local rehearsal over exact public Parquet snapshots; not deployment."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from datetime import UTC, datetime
from pathlib import Path

from rareburden.node_policy_store import DurableNodePolicyStore
from rareburden.public_node import run_public_counts

SOURCES = {
    "uci": (
        "uci-diabetes-130-us-hospitals/data/encounters.parquet",
        "cf435350273822ed4a3193e8dfd22e38bbf264839073c353cf2dda2b1fab1cb9",
    ),
    "nhanes": (
        "nhanes-2021-2023-diabetes/data/DIQ_L.parquet",
        "72404c82dcd9d9fab2233757e4b4cc97b3b2bc769e25a9d390b1d4fe2eb9242c",
    ),
}


def main() -> None:
    import pandas as pd

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inputs = {}
    for dataset, (relative, expected) in SOURCES.items():
        body = (args.source_root / relative).read_bytes()
        if hashlib.sha256(body).hexdigest() != expected:
            raise ValueError("public source hash mismatch")
        inputs[dataset] = body
    # Never reuse or reset a store. Separate rehearsal directories require explicit invocation.
    args.output.mkdir(parents=True, exist_ok=False)
    timestamp = datetime.now(UTC).isoformat()
    with DurableNodePolicyStore(args.output / "policy.sqlite3") as store:
        policy = store.register_policy(
            {
                "schema_version": "0.1.0",
                "policy_id": "public-count-policy-v1",
                "minimum_cell_count": 5,
                "max_queries_per_overlap_group": 1,
                "allowed_dimension_fields": ["group"],
                "participant_fields": ["person_id"],
                "export_mode": "aggregate_only",
            },
            recorded_at=timestamp,
        )
        results = {}
        for dataset, body in inputs.items():
            frame = pd.read_parquet(io.BytesIO(body))
            results[dataset] = run_public_counts(
                frame.to_dict("records"),
                dataset=dataset,
                source_sha256=SOURCES[dataset][1],
                store=store,
                policy_id=policy.policy_id,
                policy_sha256=policy.content_sha256,
                recorded_at=timestamp,
            )
        if store.verify() != (1, 2):
            raise ValueError("unexpected reservation count")
        # One file, exclusive creation, only after both computations succeed.
        with (args.output / "results.json").open("x") as stream:
            json.dump(results, stream, indent=2)
            stream.write("\n")
    print("Two public descriptive tables retained; no population or deployment claim.")


if __name__ == "__main__":
    main()
