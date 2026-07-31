"""Bounded Orphadata XML entity extraction for reproducible source pipelines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException

from rareburden.provenance import content_id

_TRANSFORMATION_ID = "orphadata-disorder-entities-v1"


class OrphadataXMLInvalid(ValueError):
    """Raised when an Orphadata XML release cannot be interpreted safely."""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _first_child_text(element: Any, name: str) -> str:
    for child in element.iter():
        if _local_name(str(child.tag)) == name and child.text:
            return str(child.text).strip()
    return ""


def normalise_orphadata_xml(
    path: Path,
    *,
    source_release_id: str,
    acquisition_manifest_id: str,
) -> list[dict[str, Any]]:
    """Extract ORPHA codes and preferred labels without resolving external entities."""
    try:
        root = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError, DefusedXmlException) as exc:
        raise OrphadataXMLInvalid(f"Unable to parse Orphadata XML {path}: {exc}") from exc

    records: list[dict[str, Any]] = []
    seen_codes: set[str] = set()
    for element in root.iter():
        if _local_name(str(element.tag)) != "Disorder":
            continue
        code = _first_child_text(element, "OrphaCode")
        label = _first_child_text(element, "Name")
        if not code or not label:
            continue
        if not code.isdigit():
            raise OrphadataXMLInvalid(f"Non-numeric ORPHA code encountered: {code!r}")
        if code in seen_codes:
            raise OrphadataXMLInvalid(f"Duplicate ORPHA code encountered: {code}")
        seen_codes.add(code)
        core: dict[str, Any] = {
            "schema_version": "1.0.0",
            "source_id": "orphadata-science",
            "source_release_id": source_release_id,
            "acquisition_manifest_id": acquisition_manifest_id,
            "transformation_id": _TRANSFORMATION_ID,
            "record_type": "disease_entity",
            "sex": "not_applicable",
            "measure": "disease_entity",
            "metric": "knowledge_record",
            "unit": "not_applicable",
            "evidence_status": "observed",
            "disease": {"system": "ORPHA", "code": code, "label": label},
            "attributes": {},
        }
        records.append({"record_id": content_id("rec", core), **core})
    if not records:
        raise OrphadataXMLInvalid("No Disorder elements with ORPHA code and name were found")
    return sorted(records, key=lambda item: int(item["disease"]["code"]))
