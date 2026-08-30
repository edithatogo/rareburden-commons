"""Build synthetic reference inputs, not analysis results or an execution receipt."""

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from rareburden.quality import build_evidence_assessment, build_transportability_assessment

VERSION = "RBC-P002-REFERENCE-INPUTS-v1"
DATE = "2026-08-30T00:00:00Z"


def validate_reference_inputs(candidate: dict[str, Any], root: Path) -> None:
    """Reject drift from the exact declared input-generation contract before use."""
    if candidate != build_reference_inputs(root):
        raise ValueError("reference input or authority drift; regenerate and review the candidate")


# Every number is invented for numerical assurance, not a literature extraction.
ASSUMPTIONS: dict[str, tuple[str, str, dict[str, Any], str]] = {
    "diabetes-denominator": (
        "case_count",
        "people",
        {"type": "normal", "mean": 100000.0, "standard_deviation": 2500.0, "minimum": 0.0},
        "Assumed closed cohort meeting the synthetic diabetes definition for the entire year.",
    ),
    "aetiologic-fraction": (
        "fraction",
        "proportion",
        {"type": "beta", "alpha": 2.0, "beta": 98.0},
        "Assumed expressed monogenic case fraction within the compatible diabetes denominator.",
    ),
    "carrier-person-fraction": (
        "fraction",
        "proportion",
        {"type": "beta", "alpha": 4.0, "beta": 96.0},
        "Alternative assumed person-carrier fraction within diabetes; never allele frequency.",
    ),
    "detection": (
        "fraction",
        "proportion",
        {"type": "beta", "alpha": 6.0, "beta": 4.0},
        "Forward probability of detecting an expressed synthetic case; specificity assumed one.",
    ),
    "penetrance": (
        "fraction",
        "proportion",
        {"type": "beta", "alpha": 5.0, "beta": 5.0},
        "Expression conditional on synthetic person-carrier status within diabetes only.",
    ),
    "referral-selection-ratio": (
        "other",
        "ratio",
        {"type": "fixed", "value": 2.0},
        "Assumed selection probability ratio for entity versus non-entity, aligned binary scope.",
    ),
    "young-denominator-share": (
        "fraction",
        "proportion",
        {"type": "fixed", "value": 0.25},
        "Invented age composition: ages 0-19 versus the disjoint complement ages 20-100.",
    ),
    "model-eligible-share": (
        "fraction",
        "proportion",
        {"type": "fixed", "value": 0.5},
        "Hypothetical model coverage, not an ancestry coefficient or empirical exclusion rate.",
    ),
    "unclassified-share": (
        "fraction",
        "proportion",
        {"type": "fixed", "value": 0.1},
        "Unclassified diabetes denominator share; unknown aetiology is not zero burden.",
    ),
    "diagnosis-delay": (
        "other",
        "years",
        {"type": "uniform", "lower": 1.0, "upper": 5.0},
        "Time from first joint D=1/E=1 state to detection among detected cases; "
        "not clinical onset.",
    ),
    "treatment-change": (
        "fraction",
        "proportion",
        {"type": "beta", "alpha": 4.0, "beta": 6.0},
        "Illustrative treatment change among detected cases, with no efficacy or causal claim.",
    ),
    "annual-complication": (
        "fraction",
        "proportion",
        {"type": "beta", "alpha": 2.0, "beta": 98.0},
        "One-year probability of a defined hypothetical complication in expressed cases.",
    ),
    "annual-person-cost": (
        "cost",
        "synthetic_currency_units/person_year",
        {"type": "uniform", "lower": 1000.0, "upper": 3000.0},
        "Hypothetical direct healthcare cost per expressed case-year in synthetic 2025 prices.",
    ),
    "denominator-low-scale": (
        "other",
        "ratio",
        {"type": "fixed", "value": 0.8},
        "Alternative smaller compatible diabetes envelope; not a confidence bound.",
    ),
    "denominator-high-scale": (
        "other",
        "ratio",
        {"type": "fixed", "value": 1.2},
        "Alternative larger compatible diabetes envelope; not a confidence bound.",
    ),
    "young-case-odds-ratio": (
        "other",
        "ratio",
        {"type": "fixed", "value": 0.5},
        "Invented age-specific odds contrast, not a biological or population estimate.",
    ),
    "adult-case-odds-ratio": (
        "other",
        "ratio",
        {"type": "fixed", "value": 1.5},
        "Invented complementary adult odds contrast; not an empirical transport factor.",
    ),
    "calendar-case-odds-ratio": (
        "other",
        "ratio",
        {"type": "fixed", "value": 1.25},
        "Hypothetical change for a separately labelled 2030 scenario, not a forecast.",
    ),
}


def build_reference_inputs(root: Path) -> dict[str, Any]:
    """Construct schema-compatible parameter and assessment records with closed IDs.

    Source templates supply contract structure only. Their historical receipts,
    fingerprints, dates, wording and analysis permission are not carried forward.
    This function creates candidate metadata, never authorizes or runs analysis.
    """
    ledger = yaml.safe_load((root / "examples/ledger/track-003-rbc-p002-synthetic.yml").read_text())
    evidence_template = yaml.safe_load(
        (root / "examples/quality/track-003-rbc-p002-synthetic-fraction-assessment.yml").read_text()
    )
    transport_template = yaml.safe_load(
        (
            root / "examples/quality/track-003-rbc-p002-synthetic-transportability-assessment.yml"
        ).read_text()
    )
    template = ledger["parameters"][0]
    records, evidence, transport = [], [], []
    for name, (quantity, unit, distribution, rationale) in ASSUMPTIONS.items():
        identifier = f"rbc-p002-reference-{name}"
        assessment = deepcopy(evidence_template)
        assessment.pop("assessment_id")
        assessment["subject"]["subject_id"] = identifier
        assessment["assessed_at"] = DATE
        assessment["assessor"]["identifier"] = VERSION
        assessment["domains"] = [
            {
                "domain": domain,
                "judgement": judgement,
                "rationale": description,
                "evidence_refs": [VERSION],
            }
            for domain, judgement, description in [
                ("construct_validity", "some_concern", rationale),
                (
                    "ascertainment",
                    "some_concern",
                    "Invented inputs have no empirical ascertainment or sampling frame.",
                ),
                (
                    "computational_reproducibility",
                    "low_concern",
                    "Versioned generation rules and distributions are explicit candidate inputs.",
                ),
            ]
        ]
        assessment["limitations"] = [
            "Synthetic assumption only; no clinical or empirical validity."
        ]
        assessment = build_evidence_assessment(assessment)
        transfer = deepcopy(transport_template)
        transfer.pop("assessment_id")
        transfer["parameter_id"] = identifier
        transfer["assessed_at"] = DATE
        for context in ["source_context", "target_context"]:
            transfer[context]["case_definition"] = "RBC-P002 synthetic reference definition v1"
            transfer[context]["geography"] = "synthetic-rbc-p002"
        transfer["judgement"]["uncertainty_multiplier"] = 1.0
        transfer["judgement"]["use"] = "direct"
        transfer["method"]["strategy"] = "direct_transfer"
        transfer["judgement"]["rationale"] = (
            "Identical synthetic contexts only; no empirical transportability is established."
        )
        transfer["method"]["description"] = (
            "Use only in declared synthetic scenarios; no empirical transfer "
            "or uncertainty inflation is applied."
        )
        transfer["differences"][0]["evidence_refs"] = [VERSION]
        transfer["differences"][0].update(
            materiality="negligible",
            direction="none",
            rationale="Input and reference contexts are identical fictional definitions only.",
        )
        transfer = build_transportability_assessment(transfer)
        record = deepcopy(template)
        record.update(
            parameter_id=identifier,
            label=f"Synthetic reference {name}",
            quantity_type=quantity,
            measure=rationale,
            metric=name,
            unit=unit,
            distribution=deepcopy(distribution),
            uncertainty_status="not_quantified"
            if distribution["type"] == "fixed"
            else "quantified",
            assumption_rationale=rationale,
            evidence_assessment_ids=[assessment["assessment_id"]],
            transportability_assessment_ids=[transfer["assessment_id"]],
            semantic_entity_ids=["synthetic:diabetes-reference-v1"],
            limitations=[
                "Invented for reference analysis; not evidence, a forecast or a clinical input."
            ],
        )
        record["disease_definition"]["contract_id"] = VERSION
        record["disease_definition"]["diabetes_case_definition"] = "synthetic-reference-diabetes-v1"
        records.append(record)
        evidence.append(assessment)
        transport.append(transfer)
    ledger.update(
        ledger_id="track-003-complete-reference-candidate",
        title="Synthetic reference candidate inputs",
        created_at=DATE,
        parameters=records,
        limitations=[
            "All parameters are invented assumptions; no literature result is a model input."
        ],
    )
    return {
        "candidate_version": VERSION,
        "status": "inputs_only_execution_not_authorized",
        "ledger": ledger,
        "evidence_assessments": evidence,
        "transportability_assessments": transport,
        "definition": {
            "version": VERSION,
            "geography": "synthetic-rbc-p002",
            "reference_year": 2025,
            "age_range": [0, 100],
            "sex": "all",
            "diabetes": (
                "Hypothetical membership flag D=1; not a glucose threshold or diagnostic rule."
            ),
            "carrier": (
                "Hypothetical person-level flag G=1 for synthetic:monogenic-reference; "
                "no real variant interpretation."
            ),
            "expressed_case": (
                "D=1 and aetiologic case flag E=1; carrier route additionally "
                "conditions expression on G=1."
            ),
            "detected": (
                "Expressed case and hypothetical detection flag; "
                "model state, not observed diagnosis."
            ),
            "diagnosis_delay": (
                "Historical interval from first joint synthetic D=1/E=1 state to first "
                "synthetic detection among detected cases. Not necessarily within the "
                "reference year; not age at onset or time to a genetic test."
            ),
            "annual_exposure": (
                "Closed cohort: each expressed person contributes one full case-year; "
                "no entry, exit, death or competing event during the reference year."
            ),
            "complication_eligibility": (
                "Every expressed person is assumed free of the hypothetical composite "
                "complication at year start and followed for the full year."
            ),
            "unclassified": (
                "Excluded from classified-case calculations and reported as "
                "unavailable aetiology, not zero."
            ),
            "complication": (
                "At most one hypothetical composite complication per expressed person "
                "during one year; not incidence of a named clinical endpoint."
            ),
            "cost_perspective": (
                "Direct healthcare, one-year horizon, invented 2025 currency; "
                "no discounting or broad cost-envelope allocation."
            ),
        },
        "dependence": (
            "Primary parameter draws independent by assumption; "
            "shared-versus-independent two-stratum structural scenarios required."
        ),
        "required_scenarios": [
            "primary",
            "denominator_low",
            "denominator_high",
            "ascertainment",
            "carrier_penetrance",
            "referral_selection",
            "age_stratified",
            "calendar_2030",
            "model_eligibility",
            "unclassified",
            "strata_independent",
            "strata_shared",
        ],
        "claims": dict.fromkeys(
            [
                "empirical_activation",
                "controlled_data_activation",
                "clinical_validity",
                "independent_review",
                "community_representation",
                "execution_authorized",
                "publication_authority",
                "production_release_authority",
            ],
            False,
        ),
    }
