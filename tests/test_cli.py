from __future__ import annotations

import json
from pathlib import Path

import pytest

from rareburden.__main__ import main

ROOT = Path(__file__).resolve().parents[1]


def test_version_is_available_from_installed_style_cli(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--version"])
    assert raised.value.code == 0
    assert "rareburden 0.3.0rc2" in capsys.readouterr().out


def test_doctor_json_reports_healthy_repository(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["doctor", "--root", str(ROOT), "--json"]) == 0
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["ok"] is True


@pytest.mark.parametrize("json_flag", [[], ["--json"]])
def test_estimate_cases_fails_closed(
    capsys: pytest.CaptureFixture[str], json_flag: list[str]
) -> None:
    result = main(
        [
            "estimate-cases",
            "--population",
            "1000",
            "--population-lower",
            "900",
            "--population-upper",
            "1100",
            "--fraction",
            "0.1",
            "--fraction-lower",
            "0.05",
            "--fraction-upper",
            "0.2",
            *json_flag,
        ]
    )
    assert result == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "detached numeric inputs cannot satisfy" in captured.err
    assert "use run-analysis" in captured.err
