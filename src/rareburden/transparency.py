"""Prospective protocol, analytic-decision, and deviation transparency records."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

from rareburden.provenance import content_id, sha256_file


class TransparencyRecordError(ValueError):
    """Raised when a protocol or decision record is incomplete or misleading."""


def _timestamp(value: str | None, *, field: str, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise TransparencyRecordError(f"{field} is required")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TransparencyRecordError(f"{field} must be an RFC 3339 timestamp") from exc
    if parsed.tzinfo is None:
        raise TransparencyRecordError(f"{field} must include a timezone")
    return value


def _https(value: str | None, *, field: str) -> str | None:
    if value is None:
        return None
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise TransparencyRecordError(f"{field} must be a credential-free HTTPS URL")
    return value


def _text_items(values: Sequence[str], *, field: str, allow_empty: bool = False) -> list[str]:
    cleaned = sorted({str(value).strip() for value in values if str(value).strip()})
    if not allow_empty and not cleaned:
        raise TransparencyRecordError(f"{field} must contain at least one substantive item")
    return cleaned


def build_protocol_registration(
    *,
    protocol_id: str,
    title: str,
    version: str,
    protocol_path: Path,
    logical_path: str,
    status: str,
    created_at: str,
    frozen_at: str | None,
    registration_url: str | None,
    registration_service: str | None,
    research_questions: Sequence[str],
    estimands: Sequence[str],
    planned_analyses: Sequence[str],
    exclusions: Sequence[str],
    amendments: Sequence[Mapping[str, Any]] = (),
    limitations: Sequence[str] = (),
) -> dict[str, Any]:
    """Build an immutable protocol-registration record without overstating preregistration."""
    allowed = {"draft", "internally_frozen", "externally_preregistered", "amended", "retired"}
    if status not in allowed:
        raise TransparencyRecordError(f"Unsupported protocol status: {status}")
    if protocol_path.is_symlink() or not protocol_path.is_file():
        raise TransparencyRecordError(f"Protocol snapshot is missing or unsafe: {protocol_path}")
    _timestamp(created_at, field="created_at", required=True)
    _timestamp(frozen_at, field="frozen_at")
    registration = _https(registration_url, field="registration_url")
    if status == "externally_preregistered" and (registration is None or not registration_service):
        raise TransparencyRecordError(
            "Externally preregistered protocols require a service and persistent HTTPS URL"
        )
    if status != "externally_preregistered" and registration is not None:
        raise TransparencyRecordError(
            "A registration URL may only be asserted for externally preregistered protocols"
        )
    digest, size = sha256_file(protocol_path)
    amendment_records: list[dict[str, Any]] = []
    for amendment in amendments:
        record = {
            "amendment_id": str(amendment.get("amendment_id", "")).strip(),
            "recorded_at": _timestamp(
                str(amendment.get("recorded_at", "")), field="amendment.recorded_at", required=True
            ),
            "description": str(amendment.get("description", "")).strip(),
            "rationale": str(amendment.get("rationale", "")).strip(),
            "impact": str(amendment.get("impact", "")).strip(),
            "prospective": bool(amendment.get("prospective", False)),
        }
        if not all(record[key] for key in ("amendment_id", "description", "rationale", "impact")):
            raise TransparencyRecordError(
                "Protocol amendments require id, description, rationale, and impact"
            )
        amendment_records.append(record)
    amendment_records.sort(key=lambda item: (str(item["recorded_at"]), str(item["amendment_id"])))
    core = {
        "protocol_id": protocol_id,
        "title": title,
        "version": version,
        "status": status,
        "created_at": created_at,
        "frozen_at": frozen_at,
        "registration": {
            "service": registration_service,
            "url": registration,
        },
        "protocol_snapshot": {
            "path": logical_path,
            "sha256": digest,
            "size_bytes": size,
            "media_type": "text/markdown",
        },
        "research_questions": _text_items(research_questions, field="research_questions"),
        "estimands": _text_items(estimands, field="estimands"),
        "planned_analyses": _text_items(planned_analyses, field="planned_analyses"),
        "exclusions": _text_items(exclusions, field="exclusions", allow_empty=True),
        "amendments": amendment_records,
        "limitations": _text_items(limitations, field="limitations", allow_empty=True),
    }
    return {
        "schema_version": "1.0.0",
        "protocol_registration_id": content_id("protocol", core),
        **core,
    }


def build_analysis_decision_log(
    *,
    analysis_id: str,
    protocol_registration_id: str,
    created_at: str,
    decisions: Sequence[Mapping[str, Any]],
    deviations: Sequence[Mapping[str, Any]],
    limitations: Sequence[str] = (),
) -> dict[str, Any]:
    """Build a timing-aware record of analytic choices and protocol deviations."""
    _timestamp(created_at, field="created_at", required=True)
    allowed_types = {"design", "data", "semantic", "model", "uncertainty", "quality", "reporting"}
    allowed_timing = {"prospective", "implementation", "post_hoc"}
    decision_records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for decision in decisions:
        identifier = str(decision.get("decision_id", "")).strip()
        decision_type = str(decision.get("decision_type", "")).strip()
        timing = str(decision.get("timing", "")).strip()
        if not identifier or identifier in seen:
            raise TransparencyRecordError(
                "Analysis decision identifiers must be unique and non-empty"
            )
        if decision_type not in allowed_types:
            raise TransparencyRecordError(f"Unsupported decision type: {decision_type}")
        if timing not in allowed_timing:
            raise TransparencyRecordError(f"Unsupported decision timing: {timing}")
        seen.add(identifier)
        record = {
            "decision_id": identifier,
            "decision_type": decision_type,
            "timing": timing,
            "description": str(decision.get("description", "")).strip(),
            "rationale": str(decision.get("rationale", "")).strip(),
            "consequence": str(decision.get("consequence", "")).strip(),
            "recorded_at": _timestamp(
                str(decision.get("recorded_at", "")), field="decision.recorded_at", required=True
            ),
            "status": str(decision.get("status", "accepted")).strip(),
            "evidence": sorted(
                {str(item).strip() for item in decision.get("evidence", []) if str(item).strip()}
            ),
        }
        if not all(record[key] for key in ("description", "rationale", "consequence")):
            raise TransparencyRecordError(
                f"Decision {identifier} requires description, rationale, and consequence"
            )
        if timing == "post_hoc" and not record["evidence"]:
            raise TransparencyRecordError(
                f"Post-hoc decision {identifier} requires evidence explaining why it was introduced"
            )
        decision_records.append(record)
    if not decision_records:
        raise TransparencyRecordError("At least one analytic decision is required")
    decision_records.sort(key=lambda item: (str(item["recorded_at"]), str(item["decision_id"])))

    deviation_records: list[dict[str, Any]] = []
    deviation_ids: set[str] = set()
    for deviation in deviations:
        identifier = str(deviation.get("deviation_id", "")).strip()
        if not identifier or identifier in deviation_ids:
            raise TransparencyRecordError("Deviation identifiers must be unique and non-empty")
        deviation_ids.add(identifier)
        classification = str(deviation.get("classification", "")).strip()
        if classification not in {"minor", "major", "critical"}:
            raise TransparencyRecordError(f"Unsupported deviation classification: {classification}")
        record = {
            "deviation_id": identifier,
            "classification": classification,
            "planned": str(deviation.get("planned", "")).strip(),
            "actual": str(deviation.get("actual", "")).strip(),
            "rationale": str(deviation.get("rationale", "")).strip(),
            "impact": str(deviation.get("impact", "")).strip(),
            "recorded_at": _timestamp(
                str(deviation.get("recorded_at", "")), field="deviation.recorded_at", required=True
            ),
            "resolution": str(deviation.get("resolution", "")).strip(),
        }
        if not all(
            record[key] for key in ("planned", "actual", "rationale", "impact", "resolution")
        ):
            raise TransparencyRecordError(
                f"Deviation {identifier} requires planned, actual, rationale, "
                "impact, and resolution"
            )
        deviation_records.append(record)
    deviation_records.sort(key=lambda item: (str(item["recorded_at"]), str(item["deviation_id"])))
    core = {
        "analysis_id": analysis_id,
        "protocol_registration_id": protocol_registration_id,
        "created_at": created_at,
        "decisions": decision_records,
        "deviations": deviation_records,
        "deviation_status": "none_recorded" if not deviation_records else "recorded",
        "limitations": _text_items(limitations, field="limitations", allow_empty=True),
    }
    return {
        "schema_version": "1.0.0",
        "analysis_decision_log_id": content_id("decisions", core),
        **core,
    }


def _safe_local_path(root: Path, logical_path: str) -> Path:
    path = PurePosixPath(logical_path)
    if (
        not logical_path
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in logical_path
    ):
        raise TransparencyRecordError(f"Unsafe transparency evidence path: {logical_path!r}")
    root_resolved = root.expanduser().resolve()
    candidate = root_resolved / path.as_posix()
    try:
        candidate.resolve().relative_to(root_resolved)
    except ValueError as exc:
        raise TransparencyRecordError(
            f"Transparency evidence path escapes the package root: {logical_path}"
        ) from exc
    return candidate


def verify_protocol_registration(
    registration: Mapping[str, Any],
    *,
    root: Path,
) -> list[str]:
    """Verify content identity, protocol bytes, and registration semantics."""
    failures: list[str] = []
    core = {
        key: value
        for key, value in registration.items()
        if key not in {"schema_version", "protocol_registration_id"}
    }
    try:
        expected_id = content_id("protocol", core)
    except Exception as exc:
        failures.append(f"unable to recompute protocol registration identifier: {exc}")
    else:
        if registration.get("protocol_registration_id") != expected_id:
            failures.append("protocol registration content identifier mismatch")

    status = registration.get("status")
    registration_record = registration.get("registration")
    if not isinstance(registration_record, Mapping):
        failures.append("protocol registration service record is malformed")
    else:
        service = registration_record.get("service")
        url = registration_record.get("url")
        if status == "externally_preregistered":
            if not service or not url:
                failures.append("external preregistration lacks service or URL")
            else:
                try:
                    _https(str(url), field="registration.url")
                except TransparencyRecordError as exc:
                    failures.append(str(exc))
        elif service is not None or url is not None:
            failures.append("non-preregistered protocol asserts an external registration")

    snapshot = registration.get("protocol_snapshot")
    if not isinstance(snapshot, Mapping):
        failures.append("protocol snapshot record is malformed")
        return sorted(set(failures))
    try:
        path = _safe_local_path(root, str(snapshot.get("path", "")))
    except TransparencyRecordError as exc:
        failures.append(str(exc))
        return sorted(set(failures))
    if path.is_symlink() or not path.is_file():
        failures.append(f"protocol snapshot is missing or unsafe: {snapshot.get('path')}")
        return sorted(set(failures))
    digest, size = sha256_file(path)
    if digest != snapshot.get("sha256"):
        failures.append("protocol snapshot checksum mismatch")
    if size != snapshot.get("size_bytes"):
        failures.append("protocol snapshot size mismatch")
    return sorted(set(failures))


def verify_analysis_decision_log(
    decision_log: Mapping[str, Any],
    *,
    expected_protocol_registration_id: str | None = None,
) -> list[str]:
    """Verify content identity and explicit decision/deviation state."""
    failures: list[str] = []
    core = {
        key: value
        for key, value in decision_log.items()
        if key not in {"schema_version", "analysis_decision_log_id"}
    }
    try:
        expected_id = content_id("decisions", core)
    except Exception as exc:
        failures.append(f"unable to recompute analysis decision log identifier: {exc}")
    else:
        if decision_log.get("analysis_decision_log_id") != expected_id:
            failures.append("analysis decision log content identifier mismatch")
    if (
        expected_protocol_registration_id is not None
        and decision_log.get("protocol_registration_id")
        != expected_protocol_registration_id
    ):
        failures.append("analysis decision log refers to the wrong protocol registration")
    deviations = decision_log.get("deviations")
    status = decision_log.get("deviation_status")
    if status == "none_recorded" and deviations != []:
        failures.append("deviation status says none recorded but deviations are present")
    if status == "recorded" and not deviations:
        failures.append("deviation status says recorded but no deviations are present")
    for decision in decision_log.get("decisions", []):
        if (
            isinstance(decision, Mapping)
            and decision.get("timing") == "post_hoc"
            and not decision.get("evidence")
        ):
            failures.append(
                f"post-hoc decision lacks evidence: {decision.get('decision_id', '')}"
            )
    return sorted(set(failures))


__all__ = [
    "TransparencyRecordError",
    "build_analysis_decision_log",
    "build_protocol_registration",
    "verify_analysis_decision_log",
    "verify_protocol_registration",
]
