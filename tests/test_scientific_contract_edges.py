from __future__ import annotations

import math
from copy import deepcopy
from pathlib import Path

import pytest

from rareburden.acquisition.adapters.world_bank import normalise_indicator_json
from rareburden.acquisition.download import AcquisitionError, acquire_http
from rareburden.acquisition.manifest import build_manifest
from rareburden.acquisition.normalise import (
    NormalisationError,
    build_dataset,
    validate_dataset,
    validate_observations,
    write_dataset,
    write_record_package,
)
from rareburden.landscape import (
    LandscapeValidationError,
    validate_landscape,
    validate_landscape_files,
)
from rareburden.ledger import LedgerError, _distribution_errors, validate_ledger
from rareburden.schema import load_mapping
from rareburden.stochastic import RandomStreamError, StableRandom

ROOT = Path(__file__).resolve().parents[1]
RECORD_SCHEMA_PATH = ROOT / "schemas" / "normalised-record.schema.json"
DATASET_SCHEMA_PATH = ROOT / "schemas" / "normalised-dataset.schema.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas" / "normalisation-manifest.schema.json"
LEDGER_SCHEMA = load_mapping(ROOT / "schemas" / "parameter-ledger.schema.json")
LEDGER = load_mapping(ROOT / "examples" / "ledger" / "public-foundation-synthetic.yml")
LANDSCAPE = load_mapping(ROOT / "catalog" / "initiatives.yml")
LANDSCAPE_SCHEMA = load_mapping(ROOT / "schemas" / "initiative-landscape.schema.json")
FIXTURE = ROOT / "tests" / "fixtures" / "acquisition" / "world_bank_indicator.json"


def _records() -> list[dict[str, object]]:
    return normalise_indicator_json(
        FIXTURE,
        source_release_id="fixture-release-1",
        acquisition_manifest_id="acq-0123456789abcdef01234567",
        indicator="SP.POP.TOTL",
    )


def test_normalised_observation_invariants_cover_bounds_and_age_contracts() -> None:
    schema = load_mapping(RECORD_SCHEMA_PATH)
    records = _records()
    invalid = []
    for index, mutation in enumerate(
        (
            {"upper": records[0]["value"] - 1},
            {"lower": 2, "upper": 1},
            {"age": {"start_years": 10, "end_years": 5, "open_ended": False, "label": "bad"}},
            {"age": {"start_years": 10, "end_years": 20, "open_ended": True, "label": "bad"}},
            {"age": {"start_years": 10, "end_years": None, "open_ended": False, "label": "bad"}},
        )
    ):
        record = deepcopy(records[index % len(records)])
        record["record_id"] = f"invalid-{index}"
        record.update(mutation)
        invalid.append(record)
    with pytest.raises(NormalisationError) as caught:
        validate_observations(invalid, schema)
    message = str(caught.value)
    assert "upper is below value" in message
    assert "lower exceeds upper" in message
    assert "age.start_years exceeds" in message
    assert "open-ended age" in message
    assert "closed age interval" in message


def test_normalised_dataset_lineage_schema_and_writer(tmp_path: Path) -> None:
    records = _records()
    dataset = build_dataset(
        dataset_id="dataset-fixture",
        source_release_id="fixture-release-1",
        acquisition_manifest_id="acq-0123456789abcdef01234567",
        transformation_id="world-bank-indicator-v1",
        observations=reversed(records),
        generated_at="2026-07-19T00:00:00Z",
    )
    validated = validate_dataset(dataset, DATASET_SCHEMA_PATH, RECORD_SCHEMA_PATH)
    assert [item["record_id"] for item in validated["observations"]] == sorted(
        item["record_id"] for item in records
    )
    output = tmp_path / "dataset.json"
    write_dataset(validated, output)
    assert output.is_file()

    bad_schema = deepcopy(dataset)
    bad_schema.pop("dataset_id")
    with pytest.raises(NormalisationError, match="normalised_dataset"):
        validate_dataset(bad_schema, DATASET_SCHEMA_PATH, RECORD_SCHEMA_PATH)

    bad_lineage = deepcopy(dataset)
    bad_lineage["observations"][0]["source_release_id"] = "different"
    bad_lineage["observations"][1]["acquisition_manifest_id"] = "acq-ffffffffffffffffffffffff"
    with pytest.raises(NormalisationError) as caught:
        validate_dataset(bad_lineage, DATASET_SCHEMA_PATH, RECORD_SCHEMA_PATH)
    assert "source_release_id differs" in str(caught.value)
    assert "acquisition_manifest_id differs" in str(caught.value)


def test_invalid_normalisation_manifest_removes_partial_records(tmp_path: Path) -> None:
    records = _records()
    invalid_schema = tmp_path / "manifest.schema.json"
    invalid_schema.write_text(
        '{"$schema":"https://json-schema.org/draft/2020-12/schema",'
        '"type":"object","required":["impossible"]}',
        encoding="utf-8",
    )
    output = tmp_path / "records.jsonl"
    with pytest.raises(NormalisationError, match="normalisation_manifest"):
        write_record_package(
            observations=records,
            output_path=output,
            record_schema_path=RECORD_SCHEMA_PATH,
            acquisition_manifest_id="acq-0123456789abcdef01234567",
            transformation_id="world-bank-indicator-v1",
            created_at="2026-07-19T00:00:00Z",
            manifest_schema_path=invalid_schema,
        )
    assert not output.exists()


def test_stable_random_all_parameter_guards_and_defensive_branches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for seed in (-1, 1 << 64):
        with pytest.raises(RandomStreamError, match="seed"):
            StableRandom(seed)
    for stream in (-1, 1 << 64):
        with pytest.raises(RandomStreamError, match="stream"):
            StableRandom(1, stream=stream)

    rng = StableRandom(1)
    assert rng.uniform(3.0, 3.0) == 3.0
    for bounds in ((math.inf, 1.0), (0.0, math.nan)):
        with pytest.raises(RandomStreamError, match="finite"):
            rng.uniform(*bounds)
    with pytest.raises(RandomStreamError, match="mean"):
        rng.normal(math.inf, 1)
    with pytest.raises(RandomStreamError, match="mu"):
        rng.lognormal(math.nan, 1)
    for alpha, beta, message in ((1, 0, "beta"), (math.inf, 1, "alpha")):
        with pytest.raises(RandomStreamError, match=message):
            rng.beta(alpha, beta)

    values = iter([0.0, 0.25])
    monkeypatch.setattr(rng, "random", lambda: next(values))
    assert rng._positive_random() == 0.25

    monkeypatch.setattr(rng, "gamma", lambda shape: 0.0)
    with pytest.raises(RandomStreamError, match="invalid denominator"):
        rng.beta(1, 1)


def test_ledger_distribution_edges_are_aggregated() -> None:
    errors = _distribution_errors(
        "parameter",
        {
            "type": "normal",
            "mean": math.inf,
            "standard_deviation": 0,
            "minimum": 10,
            "maximum": 1,
        },
    )
    message = "\n".join(errors)
    assert "must be finite" in message
    assert "standard_deviation must be positive" in message
    assert "minimum exceeds maximum" in message

    document = deepcopy(LEDGER)
    fraction = document["parameters"][1]
    fraction["distribution"] = {"type": "uniform", "lower": -0.1, "upper": 1.1}
    with pytest.raises(LedgerError, match="uniform fraction bounds"):
        validate_ledger(document, LEDGER_SCHEMA)


def test_landscape_file_and_additional_invariants(tmp_path: Path) -> None:
    value = deepcopy(LANDSCAPE)
    value["last_updated"] = "bad-date"
    value["decision"]["decision_date"] = "bad-date"
    value["initiatives"][0]["official_url"] = "https://user:pass@example.org/private"
    value["initiatives"][0]["last_verified"] = "bad-date"
    with pytest.raises(LandscapeValidationError) as caught:
        validate_landscape(value, LANDSCAPE_SCHEMA)
    message = str(caught.value)
    assert "last_updated" in message
    assert "decision.decision_date" in message
    assert "official_url" in message
    assert "last_verified" in message

    value = deepcopy(LANDSCAPE)
    initiative = value["initiatives"][0]
    initiative["initiative_type"] = "research_infrastructure"
    initiative["patient_level_data"] = True
    initiative["data_access"] = "not_applicable"
    with pytest.raises(LandscapeValidationError, match="not_applicable"):
        validate_landscape(value, LANDSCAPE_SCHEMA)

    broken = tmp_path / "broken.yml"
    broken.write_text("initiatives: [", encoding="utf-8")
    with pytest.raises(LandscapeValidationError):
        validate_landscape_files(broken, ROOT / "schemas" / "initiative-landscape.schema.json")


def test_compatibility_reexports_are_callable() -> None:
    assert AcquisitionError.__name__ == "AcquisitionError"
    assert callable(acquire_http)
    assert callable(build_manifest)
