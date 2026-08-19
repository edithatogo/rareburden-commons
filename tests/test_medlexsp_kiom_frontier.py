import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "docs/track-002-medlexsp-kiom-frontier-2026-08-16.json"


def load_frontier() -> dict[str, object]:
    return json.loads(FRONTIER.read_text())


def test_medlexsp_is_metadata_only_and_cloud_prohibited() -> None:
    rows = {row["source_id"]: row for row in load_frontier()["sources"]}
    medlex = rows["digital-csic-medlexsp"]
    assert medlex["artifact_identity"]["artifact_kind"] == "medical_lexicon_not_ontology"
    assert medlex["dataset_payload_observed"] is False
    assert len(medlex["observed_public_bitstreams"]) == 3
    rights = medlex["licence_disposition"]
    assert rights["public_byte_route"] == "prohibited"
    assert rights["private_hugging_face_or_cloud_route"].startswith("prohibited")
    assert rights["copy_publish_distribute_or_third_party_access_permitted"] is False


def test_medlexsp_bitstream_evidence_is_exact() -> None:
    rows = {row["source_id"]: row for row in load_frontier()["sources"]}
    bitstreams = rows["digital-csic-medlexsp"]["observed_public_bitstreams"]
    assert sum(item["size_bytes"] for item in bitstreams) == 160091
    assert all(len(item["sha256"]) == 64 for item in bitstreams)
    assert len({item["sha256"] for item in bitstreams}) == 3


def test_kiom_failed_access_cannot_be_upgraded_to_payload_or_rights() -> None:
    rows = {row["source_id"]: row for row in load_frontier()["sources"]}
    kiom = rows["kiom-traditional-korean-medicine-ontology"]
    assert kiom["artifact_identity"]["doi"] == "10.1093/bioinformatics/btq424"
    assert kiom["access_observation"]["outcome"] == "dns_resolution_failed"
    assert kiom["access_observation"]["response_bytes_observed"] == 0
    assert kiom["access_observation"]["artifact_sha256"] is None
    assert kiom["licence_disposition"]["explicit_redistribution_grant_observed"] is False
    assert kiom["licence_disposition"]["private_cloud_route"].startswith("prohibited")


def test_thematic_neighbours_are_not_duplicate_artifacts() -> None:
    payload = load_frontier()
    identities = {row["source_id"]: row for row in payload["identity_map"]}
    assert set(identities) == {
        "kiom-traditional-korean-medicine-ontology",
        "tara",
        "ocmr",
        "tcdo",
    }
    assert len({row["domain"] for row in identities.values()}) == 4
    assert all(row["duplicate_of_kiom"] is False for row in identities.values())
    assert all(value is False for value in payload["global_claims"].values())


def test_payload_bytes_are_not_committed() -> None:
    forbidden_names = {
        "TraditionalKoreanMedicine.rdf-xml.owl",
        "MedLexSp.dsv",
        "MedLexSp.xml",
    }
    committed_names = {path.name for path in ROOT.rglob("*") if path.is_file()}
    assert forbidden_names.isdisjoint(committed_names)
