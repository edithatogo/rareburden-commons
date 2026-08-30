"""Verify retained Track 003 evidence offline, without executing any analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema

from scripts.track003_reference_package import MANIFEST, candidate_manifest, digest, render_outputs
from scripts.track003_reference_runner import METRICS

COMMIT = "36f97490626747b76543f59c44220544978ef874"
TREE = "8e70545e1ffa4eb202ad444e3d68d158ce184f82"
MANIFEST_SHA = "b6f50a8b8b10bddceafd16ddaeee17e77fb6eefb8fbfd724cf747378b5a99911"
DECISION_SHA = "16ff18f14b6995139a3baca7b3ec90906e3cad128959ce176e7dbc33b0d3a4d2"
DECISION = "docs/decisions/2026-08-31-track-003-reference-execution.json"
RECEIPT = "manifests/demonstrators/track-003-reference-execution-2026-08-31.json"
RECEIPT_SHA = "7be44ac986b5eced46b1b5c3dbd7768457d869472266606ba641c5e8213a3539"
OUTPUT_DIRECTORY = "results/track-003-reference-2026-08-31"
OUTPUT_HASHES = {
    "reference-report.md": "2b1318a462c3ba05e68185e0db03c32320808e10bd82acef824659cc33cabcd2",
    "reference-results.json": "2045f12db2697d6bba280175470a878a67227a10b34a8542764119c494b9f289",
    "reference-tables.csv": "315cb384df7be9b2b65387982138f27a6c0a44b4183d12a00407c26cb21dccce",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_documents(
    receipt: dict[str, Any], decision_bytes: bytes, outputs: dict[str, bytes]
) -> None:
    """Check fixed observed identities and receipt semantics using in-memory bytes."""
    require(digest(decision_bytes) == DECISION_SHA, "approved decision bytes differ")
    decision = json.loads(decision_bytes)
    candidate = {"commit": COMMIT, "tree": TREE, "evidence_manifest_sha256": MANIFEST_SHA}
    require(decision["candidate"] == candidate, "decision candidate differs")
    require(receipt["candidate"] == candidate, "execution candidate differs")
    require(decision["owner_decision"]["status"] == "recorded", "decision not recorded")
    require(decision["owner_decision"]["selected_option_id"] == "A", "Option A not selected")
    require(receipt["decision"] == {"path": DECISION, "sha256": DECISION_SHA}, "decision link")
    require(receipt["output_directory"] == OUTPUT_DIRECTORY, "output directory differs")
    require(set(outputs) == set(OUTPUT_HASHES), "output inventory differs")
    require(
        {name: digest(data) for name, data in outputs.items()} == OUTPUT_HASHES,
        "reviewed output bytes differ",
    )
    runs = receipt["runs"]
    require(len(runs) == 2, "exactly two execution receipts required")
    require([run["role"] for run in runs] == ["primary", "separate_reproduction"], "run roles")
    require(len({run["checkout_id"] for run in runs}) == 2, "separate checkout identities")
    for run in runs:
        require(run["exit_code"] == 0, "execution failed")
        require(
            run["receipt"]
            == {
                "candidate_commit": COMMIT,
                "decision_sha256": DECISION_SHA,
                "output_sha256": OUTPUT_HASHES,
            },
            "printed execution receipt differs",
        )
    require(
        receipt["comparison"]
        == {
            "exact_inventory": True,
            "all_three_sha256_equal": True,
            "retained_analytical_variants": 1,
            "retained_execution_copies": 2,
            "extra_executions": 0,
        },
        "reproduction comparison differs",
    )
    claims = receipt["claims"]
    require(
        claims
        == {
            "synthetic_reference_execution": True,
            "owner_operated_reproduction": True,
            "empirical_validity": False,
            "controlled_data_activation": False,
            "public_aggregate_execution": False,
            "clinical_use": False,
            "independent_review": False,
            "community_representation": False,
            "production_release": False,
        },
        "unsupported execution claims",
    )
    calculation = json.loads(outputs["reference-results.json"])
    require(
        calculation["seed"] == 20260830 and calculation["iterations"] == 10000,
        "execution settings differ",
    )
    # Rendering retained summaries in memory is not another analytical execution.
    # Canonical JSON sorts keys; restore the bound report metric order explicitly.
    for scenario in calculation["scenarios"].values():
        summaries = scenario["summaries"]
        require(set(summaries) <= set(METRICS), "unknown summary metric")
        scenario["summaries"] = {name: summaries[name] for name in METRICS if name in summaries}
    rendered = render_outputs(calculation)
    require(
        {name: value.encode() for name, value in rendered.items()} == outputs,
        "report/table do not match retained results",
    )


def validate(root: Path) -> None:
    """Validate only existing evidence; no network, Git history or analytical runs."""
    root = root.resolve()

    def read(relative: str) -> bytes:
        path = root / relative
        require(path.resolve().is_relative_to(root), "path escapes repository")
        require(
            not any(
                parent.is_symlink()
                for parent in [path, *path.parents]
                if parent != root and parent.is_relative_to(root)
            ),
            "symlink evidence",
        )
        require(path.is_file(), f"missing regular evidence: {relative}")
        return path.read_bytes()

    manifest_bytes = read(MANIFEST)
    require(digest(manifest_bytes) == MANIFEST_SHA, "candidate manifest differs")
    manifest = json.loads(manifest_bytes)
    for relative, expected in manifest["files"].items():
        require(digest(read(relative)) == expected, f"bound candidate file differs: {relative}")
    require(candidate_manifest(root) == manifest, "candidate inventory differs")
    decision_bytes = read(DECISION)
    jsonschema.validate(
        json.loads(decision_bytes),
        json.loads(read("schemas/agent-owner-decision-packet.schema.json")),
    )
    output_root = root / OUTPUT_DIRECTORY
    require(output_root.is_dir() and not output_root.is_symlink(), "missing output directory")
    require({p.name for p in output_root.iterdir()} == set(OUTPUT_HASHES), "output inventory")
    outputs = {name: read(f"{OUTPUT_DIRECTORY}/{name}") for name in OUTPUT_HASHES}
    receipt_bytes = read(RECEIPT)
    require(digest(receipt_bytes) == RECEIPT_SHA, "observed execution receipt differs")
    validate_documents(json.loads(receipt_bytes), decision_bytes, outputs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    validate(args.root)
    print("Track 003 synthetic package and reproduction evidence passed; no analysis executed")


if __name__ == "__main__":
    main()
