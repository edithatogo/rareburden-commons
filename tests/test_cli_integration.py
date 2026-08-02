from __future__ import annotations

import json
import shutil
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from rareburden.__main__ import main
from rareburden.acquisition import SourceChangedError

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_ID = "acq-0123456789abcdef01234567"
SOURCE_RELEASE_ID = "fixture-release-1"


def _repository_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    root.mkdir(parents=True, exist_ok=True)
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copy2(ROOT / name, root / name)
    for name in ("catalog", "conductor", "schemas", "examples", "docs"):
        shutil.copytree(ROOT / name, root / name)
    return root


def _json_output(capsys: pytest.CaptureFixture[str]) -> dict[str, object]:
    captured = capsys.readouterr()
    assert captured.err == ""
    value = json.loads(captured.out)
    assert isinstance(value, dict)
    return value


def test_programme_document_ledger_and_analysis_commands(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repository_fixture(tmp_path)
    for command, key in (
        ("validate-catalog", "source_count"),
        ("validate-roadmap", "track_count"),
        ("validate-programme", "catalog"),
        ("doctor", "ok"),
    ):
        assert main([command, "--root", str(root), "--json"]) == 0
        assert key in _json_output(capsys)

    assert (
        main(
            [
                "validate-document",
                "--root",
                str(root),
                "--document",
                "examples/ledger/public-foundation-synthetic.yml",
                "--schema",
                "schemas/parameter-ledger.schema.json",
                "--json",
            ]
        )
        == 0
    )
    assert _json_output(capsys)["valid"] is True

    assert (
        main(
            [
                "validate-ledger",
                "--root",
                str(root),
                "--ledger",
                "examples/ledger/public-foundation-synthetic.yml",
                "--json",
            ]
        )
        == 0
    )
    assert _json_output(capsys)["parameter_count"] == 2

    output = root / "outputs" / "analysis.json"
    assert (
        main(
            [
                "run-analysis",
                "--root",
                str(root),
                "--ledger",
                "examples/ledger/public-foundation-synthetic.yml",
                "--analysis",
                "examples/analyses/expected-population-synthetic.yml",
                "--output",
                "outputs/analysis.json",
                "--created-at",
                "2026-07-19T00:00:00Z",
                "--json",
            ]
        )
        == 0
    )
    payload = _json_output(capsys)
    assert payload["created_at"] == "2026-07-19T00:00:00Z"
    assert output.is_file()


def test_source_registration_normalisation_and_gap_map_commands(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repository_fixture(tmp_path)
    fixture = root / "examples/fixtures/world-bank-synthetic.json"
    assert (
        main(
            [
                "register-release",
                "--root",
                str(root),
                "--source-id",
                "world-bank-indicators",
                "--release-id",
                "synthetic-2026-07",
                "--url",
                "https://example.org/world-bank-synthetic.json?token=secret",
                "--file",
                str(fixture),
                "--manifest",
                "outputs/world-bank.acquisition.json",
                "--source-release-record",
                "outputs/world-bank.release.json",
                "--licence-state",
                "not_applicable",
                "--json",
            ]
        )
        == 0
    )
    registration = _json_output(capsys)
    assert registration["manifest"]["requested_url"].endswith("token=REDACTED")  # type: ignore[index,union-attr]

    normalisation_cases = (
        (
            "world-bank",
            "examples/fixtures/world-bank-synthetic.json",
            ["--indicator", "NY.GDP.PCAP.CD"],
            "outputs/world-bank.dataset.json",
        ),
        (
            "population-csv",
            "examples/fixtures/un-wpp-synthetic.csv",
            [
                "--columns",
                "examples/config/un-wpp-columns.yml",
                "--multiplier",
                "1000",
                "--geography-code-system",
                "UN_M49",
            ],
            "outputs/population.dataset.json",
        ),
        (
            "who-csv",
            "examples/fixtures/who-ghe-synthetic.csv",
            ["--columns", "examples/config/who-ghe-columns.yml"],
            "outputs/who.dataset.json",
        ),
        (
            "orphadata",
            "examples/fixtures/orphadata-synthetic.xml",
            [],
            "outputs/orphadata.dataset.json",
        ),
    )
    for index, (adapter, input_path, extra, output_path) in enumerate(normalisation_cases):
        arguments = [
            "normalise-source",
            "--root",
            str(root),
            "--adapter",
            adapter,
            "--input",
            input_path,
            "--source-release-id",
            SOURCE_RELEASE_ID,
            "--acquisition-manifest-id",
            MANIFEST_ID,
            "--dataset-id",
            f"synthetic-dataset-{index}",
            "--output",
            output_path,
            "--json",
            *extra,
        ]
        assert main(arguments) == 0
        payload = _json_output(capsys)
        assert int(payload["record_count"]) >= 1
        assert (root / output_path).is_file()

    assert (
        main(
            [
                "generate-gap-map",
                "--root",
                str(root),
                "--requirements",
                "examples/config/gap-map-needs.yml",
                "--output-json",
                "outputs/gap-map.json",
                "--output-markdown",
                "outputs/gap-map.md",
                "--json",
            ]
        )
        == 0
    )
    gap_map = _json_output(capsys)
    assert len(gap_map["rows"]) == 6  # type: ignore[arg-type]
    assert (root / "outputs/gap-map.md").is_file()


def test_release_and_reference_workflows_from_cli(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repository_fixture(tmp_path)
    artefact = root / "outputs" / "result.txt"
    artefact.parent.mkdir()
    artefact.write_text("verified\n", encoding="utf-8")

    assert (
        main(
            [
                "build-release-manifest",
                "--root",
                str(root),
                "--release-id",
                "test-release",
                "--created-at",
                "2026-07-19T00:00:00Z",
                "--release-kind",
                "synthetic_assurance",
                "--data-classification",
                "synthetic",
                "--output",
                "outputs/release.json",
                "--artefact",
                "outputs/result.txt",
                "--json",
            ]
        )
        == 0
    )
    assert str(_json_output(capsys)["release_manifest_id"]).startswith("rel-")

    assert (
        main(
            [
                "verify-release-manifest",
                "--root",
                str(root),
                "--manifest",
                "outputs/release.json",
                "--json",
            ]
        )
        == 0
    )
    assert _json_output(capsys)["ok"] is True

    assert (
        main(
            [
                "demo-public-foundation",
                "--root",
                str(root),
                "--output",
                "outputs/reference",
                "--created-at",
                "2026-07-19T00:00:00Z",
                "--json",
            ]
        )
        == 0
    )
    reference = _json_output(capsys)
    assert int(reference["generated_file_count"]) >= 20

    assert (
        main(
            [
                "verify-reference-release",
                "--root",
                str(root),
                "--release",
                "outputs/reference",
                "--verified-at",
                "2026-07-19T00:00:00Z",
                "--json",
            ]
        )
        == 0
    )
    verification = _json_output(capsys)
    assert verification["status"] == "passed"
    assert verification["summary"]["passed_count"] == 7  # type: ignore[index]


def test_world_bank_plain_output_and_cli_error_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert (
        main(
            [
                "world-bank-url",
                "--country",
                "AUS",
                "--country",
                "NZL",
                "--indicator",
                "SP.POP.TOTL",
                "--year-start",
                "2020",
                "--year-end",
                "2023",
            ]
        )
        == 0
    )
    world_bank_url = capsys.readouterr().out.strip()
    assert urlsplit(world_bank_url).hostname == "api.worldbank.org"

    assert main(["doctor", "--root", str(tmp_path)]) == 1
    assert "Not a RareBurden repository root" in capsys.readouterr().err

    root = _repository_fixture(tmp_path / "fetch")
    assert (
        main(
            [
                "fetch-release",
                "--root",
                str(root),
                "--source-id",
                "fixture",
                "--release-id",
                "r1",
                "--url",
                "https://example.org/data.csv",
                "--destination",
                "outputs/data.csv",
                "--expected-sha256",
                "0" * 64,
                "--manifest",
                "outputs/data.acquisition.json",
                "--source-release-record",
                "outputs/data.release.json",
                "--licence-state",
                "not_applicable",
            ]
        )
        == 1
    )
    assert "Network acquisition is disabled" in capsys.readouterr().err


@pytest.mark.parametrize("licence_state", ["unknown", "restricted"])
def test_fetch_release_blocks_uncertain_or_restricted_licence_before_network(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    licence_state: str,
) -> None:
    root = _repository_fixture(tmp_path)
    arguments = [
        "fetch-release",
        "--root",
        str(root),
        "--source-id",
        "fixture",
        "--release-id",
        "r1",
        "--url",
        "https://example.org/data.csv",
        "--destination",
        "outputs/data.csv",
        "--expected-sha256",
        "0" * 64,
        "--manifest",
        "outputs/data.acquisition.json",
        "--source-release-record",
        "outputs/data.release.json",
        "--licence-state",
        licence_state,
        "--notes",
        "Rights require source-specific review.",
        "--allow-network",
    ]
    if licence_state == "restricted":
        arguments.extend(["--licence-reference", "https://example.org/terms"])

    assert main(arguments) == 1
    assert "prohibits automated acquisition" in capsys.readouterr().err
    assert not (root / "outputs").exists()


def test_fetch_release_records_redacted_source_change_incident(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _repository_fixture(tmp_path)

    def changed(**_kwargs: object) -> dict[str, object]:
        raise SourceChangedError(
            source_id="fixture",
            release_id="r1",
            requested_url="https://example.org/data.csv?token=secret",
            expected_sha256="0" * 64,
            observed_sha256="1" * 64,
        )

    monkeypatch.setattr("rareburden.cli.download_public_artifact", changed)
    assert (
        main(
            [
                "fetch-release",
                "--root",
                str(root),
                "--source-id",
                "fixture",
                "--release-id",
                "r1",
                "--url",
                "https://example.org/data.csv?token=secret",
                "--destination",
                "outputs/data.csv",
                "--expected-sha256",
                "0" * 64,
                "--manifest",
                "outputs/data.acquisition.json",
                "--source-release-record",
                "outputs/data.release.json",
                "--source-change-report",
                "outputs/data.source-change.json",
                "--licence-state",
                "verified",
                "--licence-reference",
                "https://example.org/terms",
                "--allow-network",
            ]
        )
        == 1
    )
    assert "Checksum mismatch" in capsys.readouterr().err
    incident = json.loads((root / "outputs/data.source-change.json").read_text(encoding="utf-8"))
    assert incident["status"] == "review_required"
    assert incident["requested_url"].endswith("token=REDACTED")
    assert "secret" not in json.dumps(incident)


@pytest.mark.parametrize(
    "source_id,release_id",
    [
        ("orphadata-science", "july-2026-pair"),
        ("un-world-population-prospects", "wpp2024-f01"),
        ("who-global-health-estimates", "ghe2021-daly-2000"),
        ("world-bank-indicators-api", "sp-pop-totl-aus-nzl-2000-2021"),
    ],
)
def test_source_change_matrix_keeps_all_track_002_candidates_fail_closed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    source_id: str,
    release_id: str,
) -> None:
    """Synthetic candidate mutations never promote changed bytes."""
    root = _repository_fixture(tmp_path)

    def changed(**_kwargs: object) -> dict[str, object]:
        raise SourceChangedError(
            source_id=source_id,
            release_id=release_id,
            requested_url="https://example.org/candidate?token=secret",
            expected_sha256="0" * 64,
            observed_sha256="1" * 64,
        )

    monkeypatch.setattr("rareburden.cli.download_public_artifact", changed)
    assert (
        main(
            [
                "fetch-release",
                "--root",
                str(root),
                "--source-id",
                source_id,
                "--release-id",
                release_id,
                "--url",
                "https://example.org/candidate?token=secret",
                "--destination",
                "outputs/data.csv",
                "--expected-sha256",
                "0" * 64,
                "--manifest",
                "outputs/data.acquisition.json",
                "--source-release-record",
                "outputs/data.release.json",
                "--source-change-report",
                "outputs/data.source-change.json",
                "--licence-state",
                "verified",
                "--licence-reference",
                "https://example.org/terms",
                "--allow-network",
            ]
        )
        == 1
    )
    assert "Checksum mismatch" in capsys.readouterr().err
    incident = json.loads((root / "outputs/data.source-change.json").read_text(encoding="utf-8"))
    assert incident["status"] == "review_required"
    assert incident["source_id"] == source_id
    assert incident["release_id"] == release_id
    assert incident["requested_url"].endswith("token=REDACTED")
    assert not (root / "outputs/data.csv").exists()
    assert "secret" not in json.dumps(incident)
