"""In-memory arithmetic assurance for Track 003, not a governed analysis runner.

All arguments are invented synthetic assumptions in one aligned diabetes
population. No source ingestion, empirical calibration, persistence or CLI is
provided. This does not extend the exactly-one-output execution disposition.
"""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class SyntheticScenario:
    """Synthetic person fractions, never allele frequencies or source observations.

    ``selection_ratio`` is P(selected | entity) / P(selected | not entity).
    Selection and classification are otherwise assumed perfect and aligned.
    For carrier scenarios selection refers to person carriers; penetrance is
    conditional on those carriers within the same diabetes denominator.
    Detection is a forward probability given a true expressed case, with no
    false positives. It is not an inversion of observed diagnosis counts.
    """

    diabetes_denominator: float
    fraction: float
    selection_ratio: float = 1.0
    detection: float = 1.0
    fraction_kind: str = "aetiologic_case_fraction"
    penetrance: float | None = None


@dataclass(frozen=True)
class SyntheticScenarioResult:
    """Deterministic assumed expectations, not observed counts or uncertainty bounds."""

    expected_people: float
    detected_people: float
    undetected_people: float
    evidence_status: str = "synthetic_assumption"
    unit: str = "people"
    uncertainty: str = "not_quantified"


def _number(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite synthetic number")
    try:
        finite = isfinite(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be representable as a finite float") from exc
    if not finite:
        raise ValueError(f"{name} must be a finite synthetic number")


def _probability(name: str, value: float) -> None:
    _number(name, value)
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be in [0, 1]")


def evaluate_synthetic_scenario(case: SyntheticScenario) -> SyntheticScenarioResult:
    """Evaluate an assumed scenario without reading or writing files.

    With selected fraction q and selection ratio r, invert
    q = r*p / (1-p+r*p) to p = q / (q+r*(1-q)). No empirical transport
    validity follows from this identity. A non-positive ratio is unsupported.
    Deterministic scenario contrasts are not confidence/credible intervals.
    """
    _number("diabetes_denominator", case.diabetes_denominator)
    if case.diabetes_denominator < 0:
        raise ValueError("diabetes_denominator must be non-negative")
    _probability("fraction", case.fraction)
    _probability("detection", case.detection)
    _number("selection_ratio", case.selection_ratio)
    if case.selection_ratio <= 0:
        raise ValueError("selection_ratio must be positive; zero is non-estimable")
    if case.fraction_kind == "carrier_person_fraction":
        if case.penetrance is None:
            raise ValueError("penetrance is required for a synthetic carrier-person fraction")
        _probability("penetrance", case.penetrance)
        expression = case.penetrance
    elif case.fraction_kind == "aetiologic_case_fraction":
        if case.penetrance is not None:
            raise ValueError("penetrance cannot be applied again to an aetiologic case fraction")
        expression = 1.0
    else:
        raise ValueError(
            "fraction_kind must be aetiologic_case_fraction or carrier_person_fraction"
        )
    q = case.fraction
    target_fraction = q / (q + case.selection_ratio * (1 - q))
    expected = case.diabetes_denominator * target_fraction * expression
    detected = expected * case.detection
    return SyntheticScenarioResult(expected, detected, expected - detected)
