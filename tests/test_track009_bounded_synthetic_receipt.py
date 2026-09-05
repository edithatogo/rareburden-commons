from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from scripts.check_track009_bounded_synthetic_receipt import (
    RECEIPT,
    SCHEMA,
    Track009SyntheticReceiptError,
    validate,
)

ROOT = Path(__file__).parents[1]


def _receipt() -> dict:
    return yaml.safe_load((ROOT / RECEIPT).read_text(encoding="utf-8"))


def _case_root(tmp_path: Path, receipt: dict) -> Path:
    for relative in (
        RECEIPT,
        SCHEMA,
        Path(receipt["candidate"]["profile_role_matrix"]),
        Path(receipt["candidate"]["manifest"]),
        Path(receipt["candidate"]["migration_receipt"]),
        Path(receipt["candidate"]["schema"]),
        Path(receipt["review_packet"]["path"]),
        Path("schemas/parameter-ledger.schema.json"),
        Path("schemas/source-profile-role-structural-assessment.schema.json"),
        Path("schemas/agent-owner-decision-packet.schema.json"),
        Path("schemas/demonstrator-ledger-profile.schema.json"),
        Path("examples/ledger/public-foundation-synthetic.yml"),
        Path("examples/ledger/economic-social-synthetic.yml"),
        Path("manifests/ledger/track-009-v0.4-public-foundation-synthetic.json"),
        Path("manifests/ledger/track-009-v0.4-economic-social-synthetic.json"),
        Path("manifests/ledger/track-009-v0.4-candidate-2026-08-21.json"),
        Path("manifests/ledger/track-009-v0.4-migration-impact-2026-08-21.json"),
        Path("docs/decisions/2026-08-21-track-009-post-merge-options.yml"),
        Path("examples/demonstrators/003-ledger-profile.yml"),
        Path("examples/demonstrators/011-ledger-profile.yml"),
        Path("examples/demonstrators/012-ledger-profile.yml"),
        Path("uv.lock"),
        Path("conductor/tracks/009-evidence-parameter-ledger/metadata.json"),
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    target = tmp_path / RECEIPT
    target.write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
    return tmp_path


def test_bounded_receipt_passes_and_keeps_global_track_bounded() -> None:
    validate(ROOT)
    receipt = _receipt()
    assert receipt["status"] == "bounded_synthetic_nonclinical_candidate_complete"
    assert all(value is False for value in receipt["claims"].values())
    assert (
        hashlib.sha256(
            (ROOT / receipt["candidate"]["profile_role_matrix"]).read_bytes()
        ).hexdigest()
        == receipt["candidate"]["profile_role_matrix_sha256"]
    )


def test_receipt_rejects_claim_drift(tmp_path: Path) -> None:
    receipt = _receipt()
    receipt["claims"]["track_complete"] = True
    with pytest.raises(ValueError, match="Schema validation failed"):
        validate(_case_root(tmp_path, receipt))


def test_receipt_rejects_candidate_hash_drift(tmp_path: Path) -> None:
    receipt = _receipt()
    receipt["candidate"]["profile_role_matrix_sha256"] = "0" * 64
    with pytest.raises(Track009SyntheticReceiptError, match="candidate hash drift"):
        validate(_case_root(tmp_path, receipt))


def test_receipt_rejects_repository_binding_drift(tmp_path: Path) -> None:
    receipt = _receipt()
    receipt["candidate"]["repository_tree"] = "0" * 40
    with pytest.raises(Track009SyntheticReceiptError, match="repository candidate binding drift"):
        validate(_case_root(tmp_path, receipt))


def test_receipt_rejects_global_blocker_removal(tmp_path: Path) -> None:
    receipt = copy.deepcopy(_receipt())
    receipt["global_blockers"].pop()
    with pytest.raises(ValueError, match="Schema validation failed"):
        validate(_case_root(tmp_path, receipt))


def test_receipt_rejects_empirical_candidate_manifest(tmp_path: Path) -> None:
    receipt = _receipt()
    root = _case_root(tmp_path, receipt)
    manifest_path = root / receipt["candidate"]["manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["claims"]["empirical_parameter_activation"] = True
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    receipt["candidate"]["manifest_sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    (root / RECEIPT).write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
    with pytest.raises(
        Track009SyntheticReceiptError,
        match=r"(overstates synthetic scope|review packet does not accept)",
    ):
        validate(root)


def test_receipt_rejects_non_accepting_panel_recommendation(tmp_path: Path) -> None:
    receipt = _receipt()
    root = _case_root(tmp_path, receipt)
    review_path = root / receipt["review_packet"]["path"]
    review = yaml.safe_load(review_path.read_text(encoding="utf-8"))
    review["recommendation"]["option_id"] = "B"
    review_path.write_text(yaml.safe_dump(review, sort_keys=False), encoding="utf-8")
    receipt["review_packet"]["sha256"] = hashlib.sha256(review_path.read_bytes()).hexdigest()
    (root / RECEIPT).write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
    with pytest.raises(Track009SyntheticReceiptError, match="review packet does not accept"):
        validate(root)


def test_receipt_rejects_ledger_regeneration_drift(tmp_path: Path) -> None:
    receipt = _receipt()
    root = _case_root(tmp_path, receipt)
    ledger_path = root / "examples/ledger/public-foundation-synthetic.yml"
    ledger_path.write_text(ledger_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(Track009SyntheticReceiptError):
        validate(root)


def test_receipt_rejects_cross_bound_candidate_artifact(tmp_path: Path) -> None:
    receipt = _receipt()
    root = _case_root(tmp_path, receipt)
    receipt["candidate"]["schema"] = receipt["candidate"]["manifest"]
    receipt["candidate"]["schema_sha256"] = receipt["candidate"]["manifest_sha256"]
    (root / RECEIPT).write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
    with pytest.raises(Track009SyntheticReceiptError, match="candidate artifact binding drift"):
        validate(root)


def test_receipt_rejects_deferred_completed_disposition(tmp_path: Path) -> None:
    receipt = _receipt()
    receipt["owner_disposition"]["decision"] = "defer_bounded_subcompletion"
    with pytest.raises(Track009SyntheticReceiptError, match="accepted bounded subcompletion"):
        validate(_case_root(tmp_path, receipt))
