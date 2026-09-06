"""Offline local rehearsal over exact public Parquet snapshots; not deployment."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import io
from datetime import UTC, datetime
from pathlib import Path

from rareburden.node_policy import SURVEY_MEASURE
from rareburden.node_policy_store import DurableNodePolicyStore
from rareburden.public_delivery import create_run_directory, recover_results, stage_results
from rareburden.public_node import run_public_counts
from rareburden.public_survey import run_public_survey

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
DEMO_SOURCE = (
    "nhanes-2021-2023-diabetes/data/DEMO_L.parquet",
    "24f3623742b1900911bc49b6fcaa0786a9eb3a486dd2d4e86a126514d427ac4f",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--recover", action="store_true")
    parser.add_argument(
        "--survey", action="store_true", help="Add the fixed adult survey candidate"
    )
    args = parser.parse_args()
    if args.recover:
        recover_results(args.output)
        print("Previously staged result delivered; no analysis rerun or budget reset.")
        return
    if args.source_root is None:
        parser.error("--source-root is required unless --recover is selected")
    pd = importlib.import_module("pandas")
    inputs = {}
    for dataset, (relative, expected) in SOURCES.items():
        body = (args.source_root / relative).read_bytes()
        if hashlib.sha256(body).hexdigest() != expected:
            raise ValueError("public source hash mismatch")
        inputs[dataset] = body
    demo_body = None
    if args.survey:
        demo_body = (args.source_root / DEMO_SOURCE[0]).read_bytes()
        if hashlib.sha256(demo_body).hexdigest() != DEMO_SOURCE[1]:
            raise ValueError("public demographics source hash mismatch")
    # Never reuse or reset a store. Separate rehearsal directories require explicit invocation.
    create_run_directory(args.output)
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
                "allowed_measures": ["count", SURVEY_MEASURE] if args.survey else ["count"],
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
        if demo_body is not None:
            results["nhanes_survey"] = run_public_survey(
                pd.read_parquet(io.BytesIO(demo_body)).to_dict("records"),
                pd.read_parquet(io.BytesIO(inputs["nhanes"])).to_dict("records"),
                demo_sha256=DEMO_SOURCE[1],
                diq_sha256=SOURCES["nhanes"][1],
                store=store,
                policy_id=policy.policy_id,
                policy_sha256=policy.content_sha256,
                recorded_at=timestamp,
            )
        if store.verify() != (1, 3 if args.survey else 2):
            raise ValueError("unexpected reservation count")
        stage_results(args.output, results)
        recover_results(args.output)
    print("Public candidate results retained; no clinical validation or deployment claim.")


if __name__ == "__main__":
    main()
