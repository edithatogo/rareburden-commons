from pathlib import Path


def test_rbc_p001d_protocol_is_explicit_and_non_binding() -> None:
    text = (Path("docs/track-005-rbc-p001d-protocol.md").read_text(encoding="utf-8")).lower()
    for phrase in (
        "non-binding preparation",
        "health-system",
        "household",
        "societal",
        "currency and price year",
        "possible or unassessed overlap blocks aggregation",
        "not_collected",
        "patient/family",
        "synthetic calculations are reference outputs only",
        "no universal monetary burden",
    ):
        assert phrase in text
