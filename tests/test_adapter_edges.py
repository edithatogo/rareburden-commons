from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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

SOURCE_RELEASE = "release-fixture"
ACQUISITION = "acq-0123456789abcdef01234567"

POPULATION_COLUMNS = {
    "geography_code": "code",
    "geography_name": "name",
    "year": "year",
    "sex": "sex",
    "age_start": "age_start",
    "age_end": "age_end",
    "age_label": "age_label",
    "value": "value",
}
WHO_COLUMNS = {
    "geography_code": "code",
    "geography_name": "name",
    "year": "year",
    "sex": "sex",
    "indicator_code": "indicator_code",
    "indicator_name": "indicator_name",
    "measure": "measure",
    "metric": "metric",
    "unit": "unit",
    "value": "value",
}


def _write_csv(path: Path, header: str, row: str | None = None) -> Path:
    content = header + "\n"
    if row is not None:
        content += row + "\n"
    path.write_text(content, encoding="utf-8")
    return path


def _population(path: Path, row: str, **kwargs: Any) -> list[dict[str, Any]]:
    _write_csv(
        path,
        "code,name,year,sex,age_start,age_end,age_label,value",
        row,
    )
    return normalise_population_csv(
        path,
        source_release_id=SOURCE_RELEASE,
        acquisition_manifest_id=ACQUISITION,
        columns=POPULATION_COLUMNS,
        **kwargs,
    )


def _who(path: Path, row: str) -> list[dict[str, Any]]:
    _write_csv(
        path,
        ("code,name,year,sex,indicator_code,indicator_name,measure,metric,unit,value"),
        row,
    )
    return normalise_who_csv(
        path,
        source_release_id=SOURCE_RELEASE,
        acquisition_manifest_id=ACQUISITION,
        columns=WHO_COLUMNS,
    )


def _world_bank_document(observations: list[Any]) -> list[Any]:
    return [{"page": 1, "pages": 1, "sourceid": "2"}, observations]


def _world_bank_observation(**changes: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
        "country": {"id": "AU", "value": "Australia"},
        "countryiso3code": "AUS",
        "date": "2023",
        "value": 26_000_000,
        "unit": "people",
        "decimal": 0,
        "obs_status": "",
    }
    result.update(changes)
    return result


def test_population_contract_and_age_label_variants(tmp_path: Path) -> None:
    no_age_columns = {
        key: value
        for key, value in POPULATION_COLUMNS.items()
        if key not in {"age_start", "age_end", "age_label"}
    }
    path = _write_csv(
        tmp_path / "all-ages.csv",
        "code,name,year,sex,value",
        "AUS,Australia,2023,both,100",
    )
    all_ages = normalise_population_csv(
        path,
        source_release_id=SOURCE_RELEASE,
        acquisition_manifest_id=ACQUISITION,
        columns=no_age_columns,
    )
    assert all_ages[0]["age"] == {
        "label": "All ages",
        "start_years": None,
        "end_years": None,
    }
    assert all_ages[0]["sex"] == "all"

    without_label = {key: value for key, value in POPULATION_COLUMNS.items() if key != "age_label"}
    path = _write_csv(
        tmp_path / "bounded.csv",
        "code,name,year,sex,age_start,age_end,value",
        "AUS,Australia,2023,female,5,9,10",
    )
    bounded = normalise_population_csv(
        path,
        source_release_id=SOURCE_RELEASE,
        acquisition_manifest_id=ACQUISITION,
        columns=without_label,
    )
    assert bounded[0]["age"]["label"] == "5-9"

    path = _write_csv(
        tmp_path / "open.csv",
        "code,name,year,sex,age_start,age_end,value",
        "AUS,Australia,2023,male,85,,10",
    )
    open_ended = normalise_population_csv(
        path,
        source_release_id=SOURCE_RELEASE,
        acquisition_manifest_id=ACQUISITION,
        columns=without_label,
    )
    assert open_ended[0]["age"]["label"] == "85+"

    path = _write_csv(
        tmp_path / "empty-bounds.csv",
        "code,name,year,sex,age_start,age_end,value",
        "AUS,Australia,2023,total,,,10",
    )
    unbounded = normalise_population_csv(
        path,
        source_release_id=SOURCE_RELEASE,
        acquisition_manifest_id=ACQUISITION,
        columns=without_label,
    )
    assert unbounded[0]["age"]["label"] == "All ages"


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("AUS,Australia,not-a-year,all,0,4,0-4,1", "Invalid population row"),
        ("AUS,Australia,1800,all,0,4,0-4,1", "Invalid year"),
        (",Australia,2023,all,0,4,0-4,1", "Missing geography"),
        ("AUS,Australia,2023,invalid,0,4,0-4,1", "Unsupported sex"),
        ("AUS,Australia,2023,all,bad,4,0-4,1", "Invalid age_start"),
        ("AUS,Australia,2023,all,-1,4,0-4,1", "Negative age_start"),
        ("AUS,Australia,2023,all,5,4,5-4,1", "age_start exceeds"),
        ("AUS,Australia,2023,all,0,4,,1", "Missing age label"),
        ("AUS,Australia,2023,all,0,4,0-4,-1", "Negative population"),
    ],
)
def test_population_rejects_invalid_rows(tmp_path: Path, row: str, message: str) -> None:
    with pytest.raises(PopulationCSVError, match=message):
        _population(tmp_path / "bad.csv", row)


def test_population_rejects_invalid_contracts_and_empty_files(tmp_path: Path) -> None:
    with pytest.raises(PopulationCSVError, match="multiplier must be positive"):
        _population(
            tmp_path / "multiplier.csv",
            "AUS,Australia,2023,all,0,4,0-4,1",
            multiplier=0,
        )

    partial = dict(POPULATION_COLUMNS)
    partial.pop("age_end")
    with pytest.raises(PopulationCSVError, match="must be supplied together"):
        normalise_population_csv(
            tmp_path / "unused.csv",
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            columns=partial,
        )

    wrong_header = _write_csv(
        tmp_path / "wrong-header.csv",
        "code,name,year,sex,age_start,age_end,age_label",
    )
    with pytest.raises(PopulationCSVError, match="lacks columns"):
        normalise_population_csv(
            wrong_header,
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            columns=POPULATION_COLUMNS,
        )

    empty = _write_csv(
        tmp_path / "empty.csv",
        "code,name,year,sex,age_start,age_end,age_label,value",
    )
    with pytest.raises(PopulationCSVError, match="contains no records"):
        normalise_population_csv(
            empty,
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            columns=POPULATION_COLUMNS,
        )

    with pytest.raises(PopulationCSVError, match="Unable to read"):
        normalise_population_csv(
            tmp_path / "missing.csv",
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            columns=POPULATION_COLUMNS,
        )


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("AUS,Australia,no,all,I,Name,deaths,count,people,1", "Invalid WHO row"),
        ("AUS,Australia,1800,all,I,Name,deaths,count,people,1", "Invalid year"),
        ("AUS,Australia,2023,bad,I,Name,deaths,count,people,1", "Unsupported sex"),
        ("AUS,Australia,2023,all,I,Name,deaths,count,people,-1", "Negative value"),
        ("AUS,Australia,2023,all,,Name,deaths,count,people,1", "Missing required text"),
    ],
)
def test_who_rejects_invalid_rows(tmp_path: Path, row: str, message: str) -> None:
    with pytest.raises(WHOCSVError, match=message):
        _who(tmp_path / "who.csv", row)


def test_who_contract_empty_and_missing_file_errors(tmp_path: Path) -> None:
    wrong_header = _write_csv(tmp_path / "wrong.csv", "code,name,year")
    with pytest.raises(WHOCSVError, match="lacks columns"):
        normalise_who_csv(
            wrong_header,
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            columns=WHO_COLUMNS,
        )

    empty = _write_csv(
        tmp_path / "empty.csv",
        ("code,name,year,sex,indicator_code,indicator_name,measure,metric,unit,value"),
    )
    with pytest.raises(WHOCSVError, match="contains no records"):
        normalise_who_csv(
            empty,
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            columns=WHO_COLUMNS,
        )

    with pytest.raises(WHOCSVError, match="Unable to read"):
        normalise_who_csv(
            tmp_path / "missing.csv",
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            columns=WHO_COLUMNS,
        )


def test_orphadata_rejects_missing_invalid_duplicate_and_empty_data(tmp_path: Path) -> None:
    missing_values = tmp_path / "missing-values.xml"
    missing_values.write_text(
        "<Root><Disorder><OrphaCode>1</OrphaCode></Disorder>"
        "<Disorder><Name>Missing code</Name></Disorder>"
        "<Disorder><OrphaCode>2</OrphaCode><Name>Valid</Name></Disorder></Root>",
        encoding="utf-8",
    )
    rows = normalise_orphadata_xml(
        missing_values,
        source_release_id=SOURCE_RELEASE,
        acquisition_manifest_id=ACQUISITION,
    )
    assert [row["disease"]["code"] for row in rows] == ["2"]

    nonnumeric = tmp_path / "nonnumeric.xml"
    nonnumeric.write_text(
        "<Root><Disorder><OrphaCode>x</OrphaCode><Name>Bad</Name></Disorder></Root>",
        encoding="utf-8",
    )
    with pytest.raises(OrphadataXMLInvalid, match="Non-numeric"):
        normalise_orphadata_xml(
            nonnumeric,
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
        )

    duplicate = tmp_path / "duplicate.xml"
    duplicate.write_text(
        "<Root><Disorder><OrphaCode>1</OrphaCode><Name>A</Name></Disorder>"
        "<Disorder><OrphaCode>1</OrphaCode><Name>B</Name></Disorder></Root>",
        encoding="utf-8",
    )
    with pytest.raises(OrphadataXMLInvalid, match="Duplicate"):
        normalise_orphadata_xml(
            duplicate,
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
        )

    empty = tmp_path / "empty.xml"
    empty.write_text("<Root />", encoding="utf-8")
    with pytest.raises(OrphadataXMLInvalid, match="No Disorder"):
        normalise_orphadata_xml(
            empty,
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
        )

    with pytest.raises(OrphadataXMLInvalid, match="Unable to parse"):
        normalise_orphadata_xml(
            tmp_path / "missing.xml",
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"countries": []},
        {"countries": ["!"]},
        {"indicator": "bad indicator"},
        {"year_start": 2025, "year_end": 2024},
        {"source": 0},
        {"per_page": 0},
    ],
)
def test_world_bank_url_rejects_invalid_arguments(kwargs: dict[str, Any]) -> None:
    arguments: dict[str, Any] = {
        "countries": ["AUS"],
        "indicator": "SP.POP.TOTL",
        "year_start": 2023,
        "year_end": 2024,
    }
    arguments.update(kwargs)
    with pytest.raises(WorldBankPayloadError):
        build_indicator_url(**arguments)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (b"\xff", "not valid UTF-8 JSON"),
        ("{", "not valid JSON"),
        ({}, "Expected"),
        ([[], []], "malformed"),
        ([{"page": "x", "pages": 1}, []], "Pagination metadata"),
        ([{"page": 2, "pages": 2}, []], "incomplete"),
        (_world_bank_document(["bad"]), "not an object"),
        (_world_bank_document([_world_bank_observation(value=True)]), "non-numeric"),
        (
            _world_bank_document([_world_bank_observation(indicator=None)]),
            "lacks indicator",
        ),
        (
            _world_bank_document(
                [_world_bank_observation(indicator={"id": "OTHER", "value": "Other"})]
            ),
            "reports 'OTHER'",
        ),
        (
            _world_bank_document([_world_bank_observation(countryiso3code="AU")]),
            "valid geography",
        ),
    ],
)
def test_world_bank_rejects_malformed_payloads(payload: Any, message: str) -> None:
    with pytest.raises(WorldBankPayloadError, match=message):
        normalise_indicator_payload(
            payload,
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            indicator="SP.POP.TOTL",
        )


def test_world_bank_skips_nulls_and_uses_fallback_metadata(tmp_path: Path) -> None:
    observation = _world_bank_observation(
        indicator={"id": "SP.POP.TOTL", "value": ""}, unit="", value=1
    )
    records = normalise_indicator_payload(
        _world_bank_document([_world_bank_observation(value=None), observation]),
        source_release_id=SOURCE_RELEASE,
        acquisition_manifest_id=ACQUISITION,
        indicator="SP.POP.TOTL",
    )
    assert records[0]["measure"] == "SP.POP.TOTL"
    assert records[0]["unit"] == "source_defined"

    with pytest.raises(WorldBankPayloadError, match="no non-null"):
        normalise_indicator_payload(
            _world_bank_document([_world_bank_observation(value=None)]),
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            indicator="SP.POP.TOTL",
        )

    malformed = tmp_path / "malformed.json"
    malformed.write_text(json.dumps({"not": "the API shape"}), encoding="utf-8")
    with pytest.raises(WorldBankPayloadError, match="Expected"):
        normalise_indicator_json(
            malformed,
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            indicator="SP.POP.TOTL",
        )

    with pytest.raises(WorldBankPayloadError, match="Unable to read"):
        normalise_indicator_json(
            tmp_path / "missing.json",
            source_release_id=SOURCE_RELEASE,
            acquisition_manifest_id=ACQUISITION,
            indicator="SP.POP.TOTL",
        )
