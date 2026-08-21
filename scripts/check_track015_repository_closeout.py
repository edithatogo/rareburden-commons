#!/usr/bin/env python3
"""Validate bounded Track 015 partnership preparation and governance tabletop."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from rareburden.schema import load_document


class Track015CloseoutError(ValueError):
    """Raised when bounded Track 015 closeout evidence drifts or overclaims."""


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_file(root: Path, relative_value: object) -> Path:
    relative = Path(str(relative_value))
    if relative.is_absolute() or ".." in relative.parts:
        raise Track015CloseoutError("evidence path is unsafe")
    path = root / relative
    if not path.is_file():
        raise Track015CloseoutError("evidence file is missing")
    return path


def validate(partnership_path: Path, tabletop_path: Path, root: Path) -> dict[str, object]:
    partnership = load_document(partnership_path)
    tabletop = load_document(tabletop_path)
    if partnership.get("status") != "bounded_non_contact_preparation":
        raise Track015CloseoutError("partnership preparation must remain non-contact")
    if partnership.get("relationship_state") != (
        "potential_complementarity_no_relationship_evidenced"
    ):
        raise Track015CloseoutError("relationship state overclaims evidence")
    targets = partnership.get("targets", [])
    if len(targets) != 6 or any(not target.get("prohibited_inference") for target in targets):
        raise Track015CloseoutError("institutional target boundaries are incomplete")
    selected = [
        option
        for option in partnership.get("sustainability_options", [])
        if option.get("status") == "selected"
    ]
    if len(selected) != 1 or selected[0].get("annual_cash_budget") != 0:
        raise Track015CloseoutError("free-tier zero-cash option must remain selected")

    if tabletop.get("status") != "completed_owner_operated_bounded_tabletop":
        raise Track015CloseoutError("tabletop completion state drifted")
    if tabletop.get("independent_or_human_review") is not False:
        raise Track015CloseoutError("tabletop cannot be independent or human review")
    if tabletop.get("public_or_external_activation") is not False:
        raise Track015CloseoutError("tabletop cannot activate an external path")
    binding = tabletop.get("policy_binding", {})
    for path_key, hash_key in (
        ("path", "sha256"),
        ("owner_disposition_path", "owner_disposition_sha256"),
    ):
        evidence = _safe_file(root, binding.get(path_key))
        if _digest(evidence) != binding.get(hash_key):
            raise Track015CloseoutError("policy evidence hash mismatch")
    geography = tabletop.get("geographic_claim_disposition", {})
    if (
        geography.get("global_claim") != "prohibited"
        or geography.get("representativeness_claim") != "prohibited"
    ):
        raise Track015CloseoutError("global or representative claim is not bounded")
    closure = tabletop.get("findings_closure", {})
    if closure.get("critical_open") != 0 or closure.get("high_open") != 0:
        raise Track015CloseoutError("blocking repository finding remains open")
    return {
        "status": "track_015_bounded_repository_closeout_valid",
        "target_count": len(targets),
        "scenario_count": len(tabletop.get("scenarios", [])),
        "external_activation": False,
        "annual_cash_budget": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("partnership", type=Path)
    parser.add_argument("tabletop", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        result = validate(args.partnership.resolve(), args.tabletop.resolve(), args.root.resolve())
    except (Track015CloseoutError, OSError, TypeError, ValueError) as exc:
        print(f"Track 015 bounded closeout failed: {exc}")
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
