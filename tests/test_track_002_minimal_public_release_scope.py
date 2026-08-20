from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
SCOPE = ROOT / "docs/track-002-minimal-public-release-scope-2026-08-20.yml"
SOURCE_EVIDENCE = ROOT / "docs/track-002-source-verification-2026-08-15.yml"


def _scope() -> dict:
    return yaml.safe_load(SCOPE.read_text(encoding="utf-8"))


def test_owner_approved_candidate_is_exact_and_preparation_only() -> None:
    scope = _scope()

    assert scope["status"] == "owner_approved_preparation_only"
    assert scope["authority"]["publication_authorized"] is False
    assert scope["authority"]["external_mutation_authorized"] is False
    assert scope["authority"]["new_private_capture_authorized"] is False

    sources = scope["candidate"]["sources"]
    assert [source["source_id"] for source in sources] == [
        "orphadata-science-july-2026",
        "mondo-v2026-08-04",
    ]
    artifacts = [artifact for source in sources for artifact in source["artifacts"]]
    assert len(artifacts) == 5
    assert all(artifact["bytes"] > 0 for artifact in artifacts)
    assert all(len(artifact["sha256"]) == 64 for artifact in artifacts)


def test_every_non_candidate_source_is_fail_closed() -> None:
    scope = _scope()
    excluded = {item["source_id"]: item for item in scope["excluded_sources"]}

    assert excluded["un-world-population-prospects"]["release_visibility"] == "private_only"
    assert excluded["un-world-population-prospects"]["existing_public_object"] is True
    assert excluded["un-world-population-prospects"]["remediation_gate"] == (
        "pending_separate_external_action_authority"
    )
    assert excluded["who-global-health-estimates"]["release_visibility"] in {
        "private_candidate",
        "metadata_only",
    }
    assert excluded["human-phenotype-ontology"]["release_visibility"] == (
        "exact_assets_only_after_separate_rights_and_release_decision"
    )
    assert excluded["panelapp-all-routes"]["release_visibility"] == "excluded"
    assert excluded["controlled-or-credentialed-sources"]["release_visibility"] == "excluded"


def test_candidate_digests_match_the_existing_exact_source_evidence() -> None:
    scope = _scope()
    evidence = yaml.safe_load(SOURCE_EVIDENCE.read_text(encoding="utf-8"))
    evidence_records = {record["source_id"]: record for record in evidence["records"]}

    candidate_artifacts = {
        artifact["name"]: (artifact["bytes"], artifact["sha256"])
        for source in scope["candidate"]["sources"]
        for artifact in source["artifacts"]
    }
    expected = {
        "en_product9_prev.xml": evidence_records["orphadata-science-epidemiology"],
        "en_product1.xml": evidence_records["orphadata-science-alignments"],
    }
    expected.update(
        {
            artifact["name"]: artifact
            for artifact in evidence_records["mondo-disease-ontology"]["artifacts"]
        }
    )
    assert candidate_artifacts == {
        name: (record["bytes"], record["sha256"]) for name, record in expected.items()
    }


def test_claims_and_release_gates_remain_bounded() -> None:
    scope = _scope()

    assert all(value is False for value in scope["claims"].values())
    gates = {gate["id"]: gate["status"] for gate in scope["release_gates"]}
    assert gates == {
        "exact_candidate_package_verification": "passed",
        "included_source_live_terms_change_exercise": "passed",
        "rights_attribution_and_third_party_audit": (
            "passed_for_exact_unmodified_candidate_with_publisher_reliance"
        ),
        "track_007_bounded_claims_dependency": "passed_for_bounded_claims_only",
        "final_owner_publication_decision": "pending",
        "wpp_existing_public_object_reconciliation": "pending_external_authority",
    }
