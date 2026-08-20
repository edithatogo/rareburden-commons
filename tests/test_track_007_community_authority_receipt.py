from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from rareburden.schema import SchemaValidationError, load_document
from scripts.check_track_007_community_authority_receipt import validate_receipt

ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "docs/track-007-community-authority-receipt-template.yml"


def _candidate() -> dict[str, object]:
    receipt = deepcopy(load_document(TEMPLATE))
    receipt.update({"receipt_id": "community-007-1", "synthetic": False})
    receipt["accountable"] = {
        "person_or_body": "Named community body",
        "self_described_role": "Delegated representative",
        "community_relationship": "Relationship stated by the submitting body",
        "organisation_or_constituency": "Named constituency",
        "authority_basis_and_scope": "Mandate for review of this candidate only",
        "contact_or_durable_record_locator": "restricted-register:record-1",
        "selection_or_quorum_basis": "Recorded selection process and quorum",
        "conflict_of_interest": "Conflicts recorded in retained evidence",
    }
    receipt["subject"] = {
        "repository": "edithatogo/rareburden-commons",
        "candidate_commit": "a" * 40,
        "manifest_id": "track-007-candidate-1",
        "manifest_sha256": "b" * 64,
    }
    receipt["review"] = {
        "materials_reviewed": ["candidate manifest", "claim language"],
        "language_and_accessibility_support": "Support process documented",
        "acceptable_use_and_harm_assessment": "Assessment recorded",
        "benefit_or_return_expectations": "Expectations recorded",
    }
    receipt["correction_and_withdrawal"] = {
        "route": "restricted-register:correction-route",
        "effect_of_correction_or_withdrawal": "Reopen gate and withdraw dependent claims",
    }
    receipt["attestation"] = {
        "submitted_by": "Named records officer",
        "submitted_at_utc": "2026-08-20T00:00:00Z",
        "signature_or_approval_record": "restricted-register:approval-1",
        "not_repository_owner_or_agent_panel_substitute": True,
        "supersedes_receipt_id": "",
    }
    return receipt


def _write(tmp_path: Path, receipt: dict[str, object]) -> Path:
    path = tmp_path / "receipt.yml"
    path.write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
    return path


def test_template_is_valid_preparation_but_cannot_qualify() -> None:
    validate_receipt(TEMPLATE)
    with pytest.raises(SchemaValidationError, match="synthetic receipt cannot qualify"):
        validate_receipt(TEMPLATE, require_qualifying=True)


def test_attributable_candidate_passes_structural_qualification(tmp_path: Path) -> None:
    validate_receipt(_write(tmp_path, _candidate()), require_qualifying=True)


@pytest.mark.parametrize("substitute", ["Repository owner", "AI agent panel"])
def test_owner_and_agent_panel_cannot_substitute(tmp_path: Path, substitute: str) -> None:
    receipt = _candidate()
    receipt["accountable"]["authority_basis_and_scope"] = substitute
    with pytest.raises(SchemaValidationError, match="disallowed substitute"):
        validate_receipt(_write(tmp_path, receipt), require_qualifying=True)


def test_placeholder_and_unbound_candidates_fail_closed(tmp_path: Path) -> None:
    receipt = _candidate()
    receipt["review"]["acceptable_use_and_harm_assessment"] = "TBD"
    with pytest.raises(SchemaValidationError, match="placeholder"):
        validate_receipt(_write(tmp_path, receipt), require_qualifying=True)
    receipt = _candidate()
    receipt["subject"]["candidate_commit"] = "main"
    with pytest.raises(SchemaValidationError, match="does not match"):
        validate_receipt(_write(tmp_path, receipt), require_qualifying=True)
