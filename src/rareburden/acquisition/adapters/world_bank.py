"""World Bank Indicators API v2 query construction and normalisation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode

from rareburden.provenance import content_id

_INDICATOR_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_COUNTRY_RE = re.compile(r"^[A-Za-z0-9_-]{2,10}$")
_TRANSFORMATION_ID = "world-bank-indicator-v1"


class WorldBankPayloadError(ValueError):
    """Raised when a World Bank response is incomplete or structurally invalid."""


def build_indicator_url(
    *,
    countries: list[str],
    indicator: str,
    year_start: int,
    year_end: int,
    source: int = 2,
    per_page: int = 20_000,
) -> str:
    """Build a canonical, bounded Indicators API v2 URL."""
    country_codes = sorted({country.strip().upper() for country in countries if country.strip()})
    if not country_codes or any(not _COUNTRY_RE.fullmatch(code) for code in country_codes):
        raise WorldBankPayloadError("countries must contain valid World Bank country codes")
    if not _INDICATOR_RE.fullmatch(indicator):
        raise WorldBankPayloadError("indicator contains unsupported characters")
    if not 1900 <= year_start <= year_end <= 2200:
        raise WorldBankPayloadError("year range is invalid")
    if source <= 0 or per_page <= 0:
        raise WorldBankPayloadError("source and per_page must be positive")
    path = (
        "https://api.worldbank.org/v2/country/"
        f"{quote(';'.join(country_codes), safe=';')}/indicator/{quote(indicator, safe='._-')}"
    )
    query = urlencode(
        {
            "date": f"{year_start}:{year_end}",
            "format": "json",
            "per_page": per_page,
            "source": source,
        }
    )
    return f"{path}?{query}"


def _load_payload(payload: bytes | str | Any) -> Any:
    if isinstance(payload, bytes):
        try:
            return json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise WorldBankPayloadError(
                f"World Bank response is not valid UTF-8 JSON: {exc}"
            ) from exc
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise WorldBankPayloadError(f"World Bank response is not valid JSON: {exc}") from exc
    return payload


def normalise_indicator_payload(
    payload: bytes | str | Any,
    *,
    source_release_id: str,
    acquisition_manifest_id: str,
    indicator: str,
) -> list[dict[str, Any]]:
    """Normalise one complete API response into aggregate records."""
    document = _load_payload(payload)
    if not isinstance(document, list) or len(document) != 2:
        raise WorldBankPayloadError("Expected [pagination metadata, observations] response")
    metadata, observations = document
    if not isinstance(metadata, dict) or not isinstance(observations, list):
        raise WorldBankPayloadError("World Bank metadata or observations are malformed")
    try:
        page = int(metadata["page"])
        pages = int(metadata["pages"])
    except (KeyError, TypeError, ValueError) as exc:
        raise WorldBankPayloadError("Pagination metadata are missing or invalid") from exc
    if page != 1 or pages != 1:
        raise WorldBankPayloadError(
            "World Bank response is incomplete; acquire and combine every page before normalising"
        )

    records: list[dict[str, Any]] = []
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            raise WorldBankPayloadError(f"Observation {index} is not an object")
        value = observation.get("value")
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise WorldBankPayloadError(f"Observation {index} has a non-numeric value")
        indicator_data = observation.get("indicator")
        country_data = observation.get("country")
        if not isinstance(indicator_data, dict) or not isinstance(country_data, dict):
            raise WorldBankPayloadError(f"Observation {index} lacks indicator or country metadata")
        observed_indicator = str(indicator_data.get("id", "")).strip()
        if observed_indicator != indicator:
            raise WorldBankPayloadError(
                f"Observation {index} reports {observed_indicator!r}, expected {indicator!r}"
            )
        geography_code = str(observation.get("countryiso3code", "")).strip().upper()
        geography_label = str(country_data.get("value", "")).strip()
        year_text = str(observation.get("date", "")).strip()
        if len(geography_code) != 3 or not geography_label or not year_text.isdigit():
            raise WorldBankPayloadError(f"Observation {index} lacks a valid geography or year")
        indicator_label = str(indicator_data.get("value", "")).strip() or indicator
        core: dict[str, Any] = {
            "schema_version": "1.0.0",
            "source_id": "world-bank-indicators",
            "source_release_id": source_release_id,
            "acquisition_manifest_id": acquisition_manifest_id,
            "transformation_id": _TRANSFORMATION_ID,
            "record_type": "indicator_estimate",
            "geography": {
                "code_system": "ISO3",
                "code": geography_code,
                "label": geography_label,
                "level": "country",
            },
            "period": {"year": int(year_text)},
            "sex": "all",
            "measure": indicator_label,
            "metric": "indicator_value",
            "unit": str(observation.get("unit") or "source_defined"),
            "value": float(value),
            "evidence_status": "observed",
            "indicator": {"code": indicator, "label": indicator_label},
            "attributes": {
                "decimal": observation.get("decimal"),
                "observation_status": str(observation.get("obs_status") or ""),
                "api_source_id": metadata.get("sourceid"),
            },
        }
        records.append({"record_id": content_id("rec", core), **core})
    if not records:
        raise WorldBankPayloadError("World Bank response contains no non-null observations")
    return sorted(records, key=lambda item: (item["geography"]["code"], item["period"]["year"]))


def normalise_indicator_json(
    path: Path,
    *,
    source_release_id: str,
    acquisition_manifest_id: str,
    indicator: str,
) -> list[dict[str, Any]]:
    """Load and normalise a cached World Bank JSON response."""
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise WorldBankPayloadError(f"Unable to read World Bank response {path}: {exc}") from exc
    return normalise_indicator_payload(
        payload,
        source_release_id=source_release_id,
        acquisition_manifest_id=acquisition_manifest_id,
        indicator=indicator,
    )
