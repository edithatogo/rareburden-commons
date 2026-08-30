"""Build an exact synthetic candidate and, only with disposition, retain its package."""

import argparse
import csv
import hashlib
import inspect
import io
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema

from rareburden.stochastic import StableRandom
from scripts.track003_reference_inputs import build_reference_inputs
from scripts.track003_reference_runner import SCENARIOS, scenario_context, simulate

MANIFEST = "manifests/demonstrators/track-003-reference-candidate.json"
OUTPUTS = ("reference-results.json", "reference-report.md", "reference-tables.csv")
EVIDENCE = (
    "docs/track-003-reference-runner-contract-2026-08-30.md",
    "docs/track-003-outcome-service-ledger-2026-08-30.yml",
    "docs/track-003-licensed-pathway-evidence-2026-08-30.yml",
    "docs/track-003-additional-source-screen-2026-08-30.md",
    "docs/track-003-reference-package-plan-2026-08-30.md",
    "docs/track-003-aetiologic-evidence-qualification-2026-08-30.yml",
    "docs/track-003-outcome-source-qualification-2026-08-30.md",
    "docs/track-003-evidence-gap-register-2026-08-30.yml",
    "docs/track-003-full-reference-acceptance-2026-08-30.md",
)

UNCERTAINTY = (
    "Invented parameter uncertainty conditional on structure, not empirical confidence; "
    "fixed design assumptions have unquantified uncertainty; zero width is not certainty."
)


def canonical(document: Any) -> str:
    """Stable UTF-8 JSON text; reject non-finite numerical serialization."""
    return json.dumps(document, sort_keys=True, indent=2, allow_nan=False) + "\n"


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def candidate_manifest(root: Path) -> dict[str, Any]:
    """Bind implementation, inputs, environment and interpretation without executing."""
    paths = {
        "pyproject.toml",
        "uv.lock",
        "schemas/agent-owner-decision-packet.schema.json",
        "scripts/track003_reference_inputs.py",
        "scripts/track003_reference_runner.py",
        "scripts/track003_reference_package.py",
        "tests/test_track003_reference_inputs.py",
        "tests/test_track003_reference_runner.py",
        "tests/test_track003_reference_package.py",
        "examples/demonstrators/track-003-reference-inputs.json",
        *EVIDENCE,
    }
    for folder, pattern in [
        ("src/rareburden", "*.py"),
        ("examples/ledger", "track-003*.yml"),
        ("examples/quality", "track-003*.yml"),
    ]:
        paths.update(str(path.relative_to(root)) for path in (root / folder).rglob(pattern))
    return {
        "version": "RBC-P002-REFERENCE-PACKAGE-v1",
        "status": "exact_candidate_execution_disposition_pending",
        "seed": 20260830,
        "iterations": 10000,
        "random_engine": "rareburden.pcg32-box-muller-marsaglia-tsang.v1",
        "environment": "uv.lock; Python 3.13; separate clean owner-operated reproduction",
        "files": {path: digest((root / path).read_bytes()) for path in sorted(paths)},
        "scenarios": {name: scenario_context(name) for name in SCENARIOS},
        "outputs": list(OUTPUTS),
        "retention": "One three-file synthetic package plus one separate reproduction copy",
        "distribution": "Public Git only after exact disposition, output review and hosted checks",
        "excluded_claims": [
            "empirical_validity",
            "controlled_data",
            "clinical_advice",
            "independent_review",
            "community_representation",
            "production_release",
        ],
    }


def render_outputs(calculation: dict[str, Any]) -> dict[str, str]:
    """Render calculation fixtures; this function grants no execution/retention authority."""
    if any(calculation["claims"].values()) or set(calculation["scenarios"]) != set(SCENARIOS):
        raise ValueError("unexpected calculation claims or scenario inventory")
    table = io.StringIO(newline="")
    writer = csv.writer(table, lineterminator="\n")
    writer.writerow(
        [
            "scenario",
            "year",
            "scope",
            "assumption",
            "metric",
            "unit",
            "conditioning_scope",
            "evidence_status",
            "deterministic",
            "mean",
            "median",
            "lower",
            "upper",
            "standard_deviation",
            "interval_interpretation",
        ]
    )
    report = [
        "# Track 003 synthetic reference report",
        "",
        "All numbers are modelled from invented assumptions, not empirical observations.",
        "This calculation/report is not an execution permission or independent validation.",
        "Clinical use, policy allocation, country rankings and ancestry biology are unsupported.",
        "",
        f"Seed: {calculation['seed']}; iterations: {calculation['iterations']}.",
        "Intervals describe invented parameter uncertainty, not empirical confidence.",
        "Deterministic values are central-input plug-ins, not nonlinear expectations.",
        "No observed diagnoses or total-population prevalence are available.",
        "Costs are fictional constant-2025 currency for one full case-year per expressed person.",
        "Complications are hypothetical, with full follow-up and no competing events.",
        "Treatment changes imply no efficacy; overlapping outcome groups must not be summed.",
        "Assumed conditional inputs remain labelled even when the conditioning set is empty.",
        UNCERTAINTY,
        "",
        "## Definitions and interpretation sources",
        "",
        "Fictional geography: synthetic-rbc-p002; ages 0-100; all sexes.",
        "D=1 denotes synthetic diabetes membership; E=1 is expressed aetiologic case status.",
        "G=1 is a person-carrier flag, not an allele frequency or clinical variant interpretation.",
        "Delay: first joint D=1/E=1 to first synthetic detection, conditional on detection.",
        "Every expressed person is assumed complication-free at year start and followed all year.",
        "Input definitions: examples/demonstrators/track-003-reference-inputs.json.",
        *[f"Interpretation evidence: {path}" for path in EVIDENCE],
        "",
    ]
    for name in SCENARIOS:
        result = calculation["scenarios"][name]
        context = result["context"]
        report.extend(
            [
                f"## {name}",
                "",
                f"Year: {context['year']}; {context['denominator_scope']}.",
                context["scenario_assumption"],
                "",
                "| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |",
                "|---|---:|---:|---:|---|",
            ]
        )
        for metric, summary in result["summaries"].items():
            metadata = result["metric_metadata"][metric]
            point = result["deterministic"][metric]
            report.append(
                f"| {metric} ({metadata['unit']}; {metadata['conditioning_scope']}) "
                f"| {point:.6g} | {summary['mean']:.6g} | {summary['median']:.6g} "
                f"| {summary['lower']:.6g} to {summary['upper']:.6g} |"
            )
            writer.writerow(
                [
                    name,
                    context["year"],
                    context["denominator_scope"],
                    context["scenario_assumption"],
                    metric,
                    metadata["unit"],
                    metadata["conditioning_scope"],
                    metadata["evidence_status"],
                    point,
                    *[
                        summary[key]
                        for key in ["mean", "median", "lower", "upper", "standard_deviation"]
                    ],
                    UNCERTAINTY,
                ]
            )
        report.append("")
    report.extend(
        [
            "## Evidence and limitations",
            "",
            "The bound runner contract contains source applicability and family dispositions.",
            "Clinical cohorts, genetic-testing duration and referral yields do not validate these",
            "fictional population probabilities, delay endpoints, outcome probabilities or prices.",
            "Source rights, correction, transport and empirical evidence gaps remain open.",
            "Unknown/uncovered burden is unavailable, not zero. No extrapolation is justified.",
            "",
        ]
    )
    return {
        "reference-results.json": canonical(calculation),
        "reference-report.md": "\n".join(report),
        "reference-tables.csv": table.getvalue(),
    }


def validate_disposition(root: Path, decision: dict[str, Any]) -> dict[str, Any]:
    """Reject pending, different-candidate or stale decisions before any simulation."""
    schema = json.loads((root / "schemas/agent-owner-decision-packet.schema.json").read_text())
    jsonschema.validate(decision, schema, format_checker=jsonschema.FormatChecker())
    identifiers = [option["id"] for option in decision["options"]]
    if decision["track_id"] != "003-monogenic-diabetes-demonstrator":
        raise ValueError("decision track is not Track 003")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("duplicate decision option IDs")
    if decision["recommendation"]["option_id"] not in identifiers:
        raise ValueError("recommendation references a missing option")
    owner = decision["owner_decision"]
    if owner["status"] != "recorded" or owner["selected_option_id"] != "A":
        raise ValueError("exact owner execution disposition is pending or not accepted")
    timestamp = owner["decided_at_utc"]
    if not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|\+00:00)",
        timestamp,
    ):
        raise ValueError("owner decision timestamp must be an explicit UTC date-time")
    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if "A" not in identifiers:
        raise ValueError("accepted option A is missing")
    option = next(item for item in decision["options"] if item["id"] == "A")
    if (
        option["disposition"] != "accept"
        or option["title"] != "Execute and retain exact synthetic package"
    ):
        raise ValueError("owner option is not the bounded execution and retention option")
    manifest_bytes = (root / MANIFEST).read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest != candidate_manifest(root):
        raise ValueError("candidate file or execution-plan drift")
    candidate = decision["candidate"]
    if candidate["evidence_manifest_sha256"] != digest(manifest_bytes):
        raise ValueError("decision manifest hash mismatch")
    for revision, expected in [("HEAD", candidate["commit"]), ("HEAD^{tree}", candidate["tree"])]:
        actual = subprocess.check_output(
            ["git", "rev-parse", revision], cwd=root, text=True
        ).strip()
        if actual != expected:
            raise ValueError("execution checkout is not the exact reviewed candidate")
    subprocess.check_output(
        ["git", "ls-files", "--error-unmatch", "--", MANIFEST, *manifest["files"]], cwd=root
    )
    if subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=root, check=False).returncode:
        raise ValueError("execution checkout has tracked file drift")
    return manifest


def validate_execution_roots(root: Path) -> None:
    """Ensure verification and the imported implementation concern the same checkout."""
    root = root.resolve()
    paths = [
        Path(__file__),
        Path(inspect.getfile(build_reference_inputs)),
        Path(inspect.getfile(simulate)),
    ]
    if any(path.resolve().parent != root / "scripts" for path in paths):
        raise ValueError("executed module root differs from verified checkout")
    if not Path(inspect.getfile(StableRandom)).resolve().is_relative_to(root / "src"):
        raise ValueError("executed random engine differs from verified checkout")


def execute(root: Path, decision_path: Path, output: Path) -> dict[str, Any]:
    """Validate, calculate, revalidate, then create one new bounded output directory."""
    validate_execution_roots(root)
    decision_bytes = decision_path.read_bytes()
    decision = json.loads(decision_bytes)
    manifest = validate_disposition(root, decision)
    if output.exists():
        raise ValueError("output directory must not exist; no overwrite or implicit replacement")
    calculation = simulate(
        build_reference_inputs(root),
        root,
        iterations=manifest["iterations"],
        seed=manifest["seed"],
    )
    outputs = render_outputs(calculation)
    if decision_path.read_bytes() != decision_bytes:
        raise ValueError("decision bytes changed during calculation")
    if validate_disposition(root, decision) != manifest:
        raise ValueError("execution manifest changed during calculation")
    output.mkdir(parents=False)
    for name in OUTPUTS:
        with (output / name).open("x", encoding="utf-8", newline="") as handle:
            handle.write(outputs[name])
    return {
        "output_sha256": {name: digest(text.encode()) for name, text in outputs.items()},
        "decision_sha256": digest(decision_bytes),
        "candidate_commit": decision["candidate"]["commit"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(canonical(execute(args.root, args.decision, args.output)), end="")


if __name__ == "__main__":
    main()
