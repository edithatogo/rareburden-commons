from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).parents[1]
DECISION = Path("docs/decisions/2026-08-21-track-010-synthetic-candidate-disposition.yml")
TRACK009_COMPLETION = Path(
    "docs/decisions/2026-08-26-track-009-bounded-completion-authorization.yml"
)
SCHEMA = Path("schemas/agent-owner-decision-packet.schema.json")
READINESS = Path("docs/track-010-alpha-freeze-readiness-2026-08-21.yml")


def test_owner_disposition_is_schema_valid_and_selects_option_a() -> None:
    schema = json.loads((ROOT / SCHEMA).read_text(encoding="utf-8"))
    document = yaml.safe_load((ROOT / DECISION).read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(document)
    assert document["owner_decision"]["status"] == "recorded"
    assert document["owner_decision"]["selected_option_id"] == "A"
    assert document["owner_decision"]["decided_by"] == "edithatogo"


def test_owner_disposition_preserves_every_dependency_and_freeze_gate() -> None:
    document = yaml.safe_load((ROOT / READINESS).read_text(encoding="utf-8"))
    disposition = document["bounded_owner_disposition"]
    assert disposition["status"] == "authorized_disposable_synthetic_pre_alpha_only"
    assert disposition["governance_status"] == "owner_operated_not_independent_review"
    assert document["upstream_dependency"]["state"] == "satisfied"
    assert document["upstream_dependency"]["completion_decision"] == (
        TRACK009_COMPLETION.as_posix()
    )
    assert document["upstream_dependency"]["completion_scope"] == (
        "bounded synthetic and exactly-receipted public-aggregate contract only"
    )
    assert document["upstream_dependency"]["prohibited_effects"] == [
        "empirical_parameter_activation",
        "controlled_data_activation",
        "independent_review",
        "publication_authority",
        "release_authority",
    ]
    assert document["review_gate"]["state"] == "pending"
    assert document["alpha_freeze_gate"]["state"] == "pending"
    assert set(document["claims"].values()) == {False}
