from __future__ import annotations

import json
from pathlib import Path

import pytest

from rareburden.acquisition.adapters.csv_population import (
    PopulationCSVError,
    normalise_population_csv,
)
from rareburden.acquisition.adapters.orphadata import (
    OrphadataXMLInvalid,
    normalise_orphadata_xml,
)
from rareburden.acquisition.adapters.who import WHOCSVError, normalise_who_csv
from rareburden.acquisition.adapters.world_bank import (
    WorldBankPayloadError,
    build_indicator_url,
    normalise_indicator_json,
    normalise_indicator_payload,
)
from rareburden.normalization import NormalizationError, validate_records, write_record_package
from rareburden.schema import load_mapping

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "acquisition"
RECORD_SCHEMA = ROOT / "schemas" / "normalised-record.schema.json"
PACKAGE_SCHEMA = ROOT / "schemas" / "normalisation-manifest.schema.json"
MANIFEST_ID = "acq-0123456789abcdef01234567"
SOURCE_RELEASE_ID = "fixture-release-1"


def test_world_bank_url_is_canonical_and_explicit() -> None:
    url = build_indicator_url(
        countries=["NZL", "AUS", "AUS"],
        indicator="SP.POP.TOTL",
        year_start=2022,
        year_end=2023,
    )
    assert "/country/AUS;NZL/indicator/SP.POP.TOTL" in url
    assert "date=2022%3A2023" in url
    assert "format=json" in url
    assert "source=2" in url


def test_world_bank_fixture_normalises_and_validates(tmp_path: Path) -> None:
    rows = normalise_indicator_json(
        FIXTURES / "world_bank_indicator.json",
        source_release_id=SOURCE_RELEASE_ID,
        acquisition_manifest_id=MANIFEST_ID,
        indicator="SP.POP.TOTL",
    )
    assert sorted(row["geography"]["code"] for row in rows) == ["AUS", "NZL"]
    assert {row["value"] for row in rows} == {26_638_544.0, 5_228_100.0}

    output = tmp_path / "world-bank.jsonl"
    _, manifest_path, manifest = write_record_package(
        records=rows,
        output_path=output,
        schema_path=RECORD_SCHEMA,
        acquisition_manifest_id=MANIFEST_ID,
        transformation_id="world-bank-indicator-v1",
        created_at="2026-07-19T00:00:00Z",
        manifest_schema_path=PACKAGE_SCHEMA,
    )
    assert manifest["record_count"] == 2
    assert len(output.read_text(encoding="utf-8").splitlines()) == 2
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["records_sha256"]


def test_world_bank_rejects_incomplete_pagination() -> None:
    with pytest.raises(WorldBankPayloadError, match="incomplete"):
        normalise_indicator_payload(
            [{"page": 1, "pages": 2}, []],
            source_release_id=SOURCE_RELEASE_ID,
            acquisition_manifest_id=MANIFEST_ID,
            indicator="SP.POP.TOTL",
        )


def test_population_fixture_uses_declared_contract_and_multiplier() -> None:
    rows = normalise_population_csv(
        FIXTURES / "population.csv",
        source_release_id=SOURCE_RELEASE_ID,
        acquisition_manifest_id=MANIFEST_ID,
        columns={
            "geography_code": "Location code",
            "geography_name": "Location",
            "year": "Year",
            "sex": "Sex",
            "age_start": "AgeStart",
            "age_end": "AgeEnd",
            "age_label": "AgeLabel",
            "value": "PopulationThousands",
        },
        multiplier=1000.0,
    )
    validate_records(rows, load_mapping(RECORD_SCHEMA))
    australia = next(row for row in rows if row["geography"]["code"] == "AUS")
    assert australia["value"] == 1_642_500.0
    assert australia["age"]["label"] == "0-4"


def test_population_rejects_implicit_or_bad_columns(tmp_path: Path) -> None:
    with pytest.raises(PopulationCSVError, match="Missing column mappings"):
        normalise_population_csv(
            FIXTURES / "population.csv",
            source_release_id=SOURCE_RELEASE_ID,
            acquisition_manifest_id=MANIFEST_ID,
            columns={"year": "Year"},
        )

    malformed = tmp_path / "malformed.csv"
    malformed.write_text(
        "Code,Name,Year,AgeStart,AgeEnd,AgeLabel,Sex,Value\nAUS,Australia,2023,0,4,0-4,all,-1\n",
        encoding="utf-8",
    )
    with pytest.raises(PopulationCSVError, match="Negative population"):
        normalise_population_csv(
            malformed,
            source_release_id=SOURCE_RELEASE_ID,
            acquisition_manifest_id=MANIFEST_ID,
            columns={
                "geography_code": "Code",
                "geography_name": "Name",
                "year": "Year",
                "age_start": "AgeStart",
                "age_end": "AgeEnd",
                "age_label": "AgeLabel",
                "sex": "Sex",
                "value": "Value",
            },
        )


def test_orphadata_and_who_fixtures_normalise_and_validate(tmp_path: Path) -> None:
    disease_rows = normalise_orphadata_xml(
        FIXTURES / "orphadata.xml",
        source_release_id=SOURCE_RELEASE_ID,
        acquisition_manifest_id=MANIFEST_ID,
    )
    who_rows = normalise_who_csv(
        FIXTURES / "who.csv",
        source_release_id=SOURCE_RELEASE_ID,
        acquisition_manifest_id=MANIFEST_ID,
        columns={
            "geography_code": "geography_code",
            "geography_name": "geography_name",
            "year": "year",
            "sex": "sex",
            "indicator_code": "cause_code",
            "indicator_name": "cause_name",
            "measure": "measure",
            "metric": "metric",
            "unit": "unit",
            "value": "value",
        },
    )
    schema = load_mapping(RECORD_SCHEMA)
    assert len(validate_records(disease_rows, schema)) == 2
    assert len(validate_records(who_rows, schema)) == 2
    assert {row["disease"]["code"] for row in disease_rows} == {"244", "791"}

    malicious = tmp_path / "malicious.xml"
    malicious.write_text(
        '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><JDBOR>&xxe;</JDBOR>',
        encoding="utf-8",
    )
    with pytest.raises(OrphadataXMLInvalid, match="parse"):
        normalise_orphadata_xml(
            malicious,
            source_release_id=SOURCE_RELEASE_ID,
            acquisition_manifest_id=MANIFEST_ID,
        )


def test_who_requires_explicit_mapping() -> None:
    with pytest.raises(WHOCSVError, match="Missing column mappings"):
        normalise_who_csv(
            FIXTURES / "who.csv",
            source_release_id=SOURCE_RELEASE_ID,
            acquisition_manifest_id=MANIFEST_ID,
            columns={"year": "year"},
        )


def test_record_bounds_duplicate_ids_and_lineage_fail_closed(tmp_path: Path) -> None:
    rows = normalise_indicator_json(
        FIXTURES / "world_bank_indicator.json",
        source_release_id=SOURCE_RELEASE_ID,
        acquisition_manifest_id=MANIFEST_ID,
        indicator="SP.POP.TOTL",
    )
    rows[0]["lower"] = rows[0]["value"] + 1
    with pytest.raises(NormalizationError, match="lower exceeds value"):
        validate_records(rows, load_mapping(RECORD_SCHEMA))

    rows = normalise_indicator_json(
        FIXTURES / "world_bank_indicator.json",
        source_release_id=SOURCE_RELEASE_ID,
        acquisition_manifest_id=MANIFEST_ID,
        indicator="SP.POP.TOTL",
    )
    with pytest.raises(NormalizationError, match="duplicate record_id"):
        validate_records([rows[0], rows[0]], load_mapping(RECORD_SCHEMA))

    with pytest.raises(NormalizationError, match="transformation_id"):
        write_record_package(
            records=rows,
            output_path=tmp_path / "bad.jsonl",
            schema_path=RECORD_SCHEMA,
            acquisition_manifest_id=MANIFEST_ID,
            transformation_id="wrong-transform-v1",
            created_at="2026-07-19T00:00:00Z",
        )
