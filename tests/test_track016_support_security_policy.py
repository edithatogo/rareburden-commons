from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs/track-016-support-security-fix-policy.md"


def test_security_entrypoint_routes_private_reports_to_bounded_policy() -> None:
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    normalized = " ".join(security.split())
    assert "docs/track-016-support-security-fix-policy.md" in security
    assert "https://github.com/edithatogo/rareburden-commons/security/advisories/new" in security
    assert "current `main` branch" in normalized
    assert "do not receive continuing fixes" in normalized


def test_support_policy_preserves_owner_backup_and_service_boundaries() -> None:
    policy = POLICY.read_text(encoding="utf-8")
    normalized = " ".join(policy.split())
    required = {
        "`edithatogo`",
        "`owner_attested_private_backup_acceptance`",
        "hash-bound handoff evidence remain incomplete",
        "Owner-operated restore tests do not complete that handoff",
        "No response-time, restoration-time, availability or service-level commitment",
        "do not prove continuous monitoring, staffed response, independent review",
        "Python 3.13 remains the release-build and cross-platform portability runtime",
        "does not complete the separate qualifying backup handoff",
        "Track 016 remains Planned",
    }
    missing = sorted(fragment for fragment in required if fragment not in normalized)
    assert not missing, f"support/security policy lost fail-closed boundaries: {missing}"


def test_track_plan_separates_bounded_policy_from_non_authorising_recovery() -> None:
    plan = (ROOT / "conductor/tracks/016-security-reliability-operations/plan.md").read_text(
        encoding="utf-8"
    )
    assert "- [x] Publish the bounded support and security-fix policy" in plan
    assert "- [x] Supersede the proposed private backup-owner role" in plan
    assert "recovery controls that confer no" in plan
    assert "owner-incapacity, credential-compromise" in plan
