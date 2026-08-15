import hashlib
import subprocess
from pathlib import Path

from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/track-007-registration-challenge-readiness-2026-08-04.yml"
REFRESHED_PACKET = ROOT / "docs/track-007-registration-challenge-readiness-2026-08-15.yml"
REPOSITORY_REGISTRATION = ROOT / "docs/track-007-repository-registration-2026-08-16.yml"
CHALLENGE_TASK = ROOT / "docs/track-007-agent-challenge-task-2026-08-16.yml"


def test_track_007_readiness_packet_is_fail_closed() -> None:
    packet = load_mapping(PACKET)
    assert packet["status"] == "repository_owned_readiness_pending_external_receipts"
    assert packet["submission_readiness"]["status"] == "deferred_by_owner"
    assert packet["protocol"]["frozen_protocol_hash"].startswith("sha256:")
    assert packet["protocol"]["search_strategy_hash"].startswith("sha256:")
    assert packet["methods_challenge"]["status"].endswith("independent_receipt")
    assert packet["patient_community_interpretation"]["status"].endswith("accountable_receipt")


def test_track_007_readiness_disables_unqualified_claims() -> None:
    claims = set(load_mapping(PACKET)["claim_boundary"]["disabled_until_receipts"])
    assert {
        "comprehensive landscape",
        "global completeness",
        "independent novelty confirmation",
    } <= claims


def test_refreshed_track_007_packet_binds_evidence_and_keeps_receipts_pending() -> None:
    packet = load_mapping(REFRESHED_PACKET)
    assert packet["protocol"]["version"] == "0.2.0"
    for field in ("source_packet_sha256", "search_log_sha256", "screening_register_sha256"):
        assert packet["protocol"][field].startswith("sha256:")
    assert packet["registration"]["status"] == "repository_hash_registered"
    assert packet["registration"]["osf"] == "deferred_by_owner"
    assert packet["methods_challenge"]["status"].endswith("agent_findings")
    assert packet["patient_community_interpretation"]["status"].endswith("agent_findings")
    disabled = set(packet["claim_boundary"]["disabled_after_owner_disposition"])
    assert "completed systematic or scoping review" in disabled
    assert "independently confirmed novelty" in disabled


def test_repository_registration_is_content_addressed_and_reconstructable() -> None:
    registration = load_mapping(REPOSITORY_REGISTRATION)
    assert registration["status"] == "repository_hash_registered"
    assert registration["repository"]["external_registry"] == "optional_deferred"
    assert registration["repository"]["osf"] == "removed_from_active_plan"

    records = [registration["protocol"], *registration["evidence"]]
    for record in records:
        path = ROOT / record["path"]
        assert path.is_file()
        payload = path.read_bytes()
        assert hashlib.sha256(payload).hexdigest() == record["sha256"]
        blob_oid = subprocess.run(
            ["git", "hash-object", str(path)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert blob_oid == record["git_blob_oid"]


def test_frozen_protocol_keeps_claims_and_osf_fail_closed() -> None:
    protocol = (ROOT / "docs/track-007-protocol-v0.2.0.md").read_text()
    assert "OSF is deferred by owner decision" in protocol
    assert "not a census" in protocol
    assert "Comprehensive coverage" in protocol
    prohibited = set(load_mapping(REPOSITORY_REGISTRATION)["claim_boundary"]["prohibited"])
    assert {
        "completed systematic or scoping review",
        "comprehensive or globally representative coverage",
        "independent novelty confirmation",
        "patient or community approval",
    } <= prohibited


def test_agent_challenge_task_binds_inputs_and_separates_roles() -> None:
    task = load_mapping(CHALLENGE_TASK)
    assert task["assurance"] == "advisory_role_separated_agent_challenge"
    assert {role["role_id"] for role in task["roles"]} == {
        "methods_coverage_challenger",
        "community_harm_equity_challenger",
        "adversarial_claim_auditor",
    }
    for record in task["candidate"].values():
        if not isinstance(record, dict) or "path" not in record:
            continue
        payload = (ROOT / record["path"]).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == record["sha256"]
    assert task["owner_boundary"] == "panel_advises_repository_owner_records_disposition"
    assert (
        "claim independent, human, patient, community, institutional or external review"
        in task["prohibited_actions"]
    )
