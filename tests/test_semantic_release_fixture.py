from pathlib import Path

from rareburden.schema import load_mapping
from rareburden.semantics import load_mapping_set, render_mapping_release_markdown

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_machine_and_human_readable_release_stay_in_sync() -> None:
    mapping_path = ROOT / "examples/semantics/orpha-to-synthetic-mapping.yml"
    release_path = ROOT / "examples/semantics/releases/orpha-to-synthetic-v0.1.0.md"
    mapping = load_mapping_set(mapping_path, ROOT / "schemas/ontology-mapping.schema.json")
    rendered = render_mapping_release_markdown(mapping)
    assert release_path.read_text(encoding="utf-8") == rendered
    assert load_mapping(mapping_path)["source_version"] == "fixture-2026-08"
