#!/usr/bin/env python3
"""Validate the bounded Track 013 real-public aggregate validation tranche."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

BRONCH = Path("examples/empirical/track-261-idiopathic-bronchiectasis-finland.csv")
PAED = Path("examples/empirical/track-012-world-bank-australia-paediatric-denominator-2023.csv")
EXPECTED = {
    BRONCH: "15394abd47fbd9ae47e1c401379cfb5ffc960be2b6a0ef7a6fbf28bc2ba72c47",
    PAED: "5da568a66d63210b1841e85adf111cbac1767d89ebe5cd8a29c7defa2e07450d",
}


class Track013RealValidationError(ValueError):
    """Raised when exact empirical evidence or scope claims drift."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path) -> dict[str, Any]:
    for relative, expected in EXPECTED.items():
        path = root / relative
        if not path.is_file() or sha256(path) != expected:
            raise Track013RealValidationError(f"exact input hash mismatch: {relative}")

    with (root / BRONCH).open(newline="", encoding="utf-8") as handle:
        bronch_rows = list(csv.DictReader(handle))
    if len(bronch_rows) != 1:
        raise Track013RealValidationError("bronchiectasis extract must contain one row")
    bronch = bronch_rows[0]
    if (bronch["geography"], bronch["measure"], bronch["value"], bronch["unit"]) != (
        "Finland",
        "annual incidence",
        "1.8",
        "cases per 100000 population per year",
    ):
        raise Track013RealValidationError("bronchiectasis observation drift")

    with (root / PAED).open(newline="", encoding="utf-8") as handle:
        paed_rows = list(csv.DictReader(handle))
    if len(paed_rows) != 1 or paed_rows[0]["country_iso3"] != "AUS":
        raise Track013RealValidationError("paediatric denominator scope drift")
    if paed_rows[0]["derived_population_age_0_14"] != "4806859.370189":
        raise Track013RealValidationError("paediatric derived denominator drift")

    return {
        "status": "bounded_real_public_aggregate_validation_pass",
        "inputs": {str(path): sha256(root / path) for path in EXPECTED},
        "triangulation": {
            "bronchiectasis": "same-source descriptive consistency only; no independent validation",
            "paediatric": "denominator arithmetic consistency only; not a disease estimate",
            "overlap": "Track 010 and Track 011 intentionally reuse the same Orphadata record; not independent evidence",
        },
        "bias": ["historical hospital-discharge ascertainment", "unknown age/sex and observation-period detail", "aggregate denominator is not disease ascertainment"],
        "equity": {"absent": ["Indigenous status", "subnational populations", "people outside recorded care", "actual patient/community voice"], "harm": ["misreading a denominator as a cohort", "transporting Finland incidence to Australia", "overinterpreting aggregate counts"]},
        "transportability": "not_estimable; Finland incidence and Australian population denominator are not combined",
        "uncertainty": "not quantified for the source observations; missing intervals and age/sex detail remain explicit",
        "decision_sensitivity": {"activation": "any missing exact hash, rights, fitness or review receipt keeps empirical activation false", "release": "any unresolved critical assurance gate blocks atlas/release claims"},
        "claims": {"empirical_validation": False, "clinical_validation": False, "equity_sufficiency": False, "global_representativeness": False, "production_activation": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.root.resolve())
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
