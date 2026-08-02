from __future__ import annotations

from pathlib import Path

import pytest

from rareburden.schema import SchemaValidationError
from scripts.check_external_receipt import validate_receipt

ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "docs/external-gate-receipt-template.yml"


def test_receipt_validator_accepts_shape_but_rejects_blank_attribution() -> None:
    validate_receipt(TEMPLATE)
    with pytest.raises(SchemaValidationError, match="not attributable"):
        validate_receipt(TEMPLATE, require_attributable=True)
