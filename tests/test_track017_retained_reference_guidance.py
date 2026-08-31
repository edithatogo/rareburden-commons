"""Guard the documented read-only route without repeating analytical execution."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERIFY_COMMAND = "uv run python -m scripts.check_track003_reference_closeout --root ."


@pytest.mark.parametrize(
    "relative",
    ["docs/tutorial-reference-workflow.md", "docs/guides/analyst.md"],
)
def test_retained_inspection_is_separate_from_foundation_generation(relative: str) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    sections = re.split(r"^## ", text, flags=re.MULTILINE)
    inspection = next(section for section in sections if section.startswith("Inspect"))
    generation = next(section for section in sections if section.startswith("Generate"))
    assert VERIFY_COMMAND in inspection
    assert VERIFY_COMMAND not in generation
    assert "public-foundation" in generation
    commands = "\n".join(re.findall(r"```(?:bash|sh)\n(.*?)```", inspection, re.DOTALL))
    assert "demo-public-foundation" not in commands
    assert "track003_reference_package" not in commands
    assert "--overwrite" not in commands
    normalized = " ".join(inspection.lower().split())
    assert "not new analytical-run authorization" in normalized
    assert "stop" in normalized
    assert "not regenerate" in normalized


@pytest.mark.parametrize(
    "relative",
    ["docs/tutorial-reference-workflow.md", "docs/guides/analyst.md"],
)
def test_retained_inspection_requires_checkout_not_installed_projection(relative: str) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    normalized = " ".join(text.lower().split())
    assert "full repository checkout" in normalized
    assert "`results/`" in text and "`manifests/`" in text
    assert (
        "not just an installed wheel" in normalized
        or "not included in the installed-wheel documentation projection" in normalized
    )
    assert "track-003-reference-closeout-2026-08-31.md" in text


def test_tutorial_identifies_retained_output_inventory_and_interpretation() -> None:
    text = (ROOT / "docs/tutorial-reference-workflow.md").read_text(encoding="utf-8")
    retained = ROOT / "results/track-003-reference-2026-08-31"
    assert {path.name for path in retained.iterdir()} == {
        "reference-report.md",
        "reference-results.json",
        "reference-tables.csv",
    }
    assert "results/track-003-reference-2026-08-31/" in text
    for path in retained.iterdir():
        assert f"`{path.name}`" in text
    normalized = " ".join(text.lower().split())
    for boundary in (
        "all inputs are invented",
        "unavailable burden is not zero",
        "not independent validation",
        "production release are not established",
    ):
        assert boundary in normalized
