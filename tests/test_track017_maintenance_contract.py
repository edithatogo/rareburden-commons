from pathlib import Path


def test_retained_reference_maintenance_contract_preserves_boundaries() -> None:
    text = (
        Path("docs/track-017-retained-reference-maintenance-2026-09-04.md")
        .read_text(encoding="utf-8")
        .lower()
    )
    for phrase in (
        "source of truth",
        "immutable reference",
        "inspection must not",
        "hash-bound notices",
        "no adoption or release claim",
        "controlled-data access",
        "green validation suite is repository readiness only",
        "stop and route to owner disposition",
    ):
        assert phrase in text
