"""Fail-closed ledger readiness checks for non-binding demonstrator profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rareburden.ledger import ParameterLedger


class DemonstratorReadinessError(ValueError):
    """Raised when a demonstrator profile is internally inconsistent."""


@dataclass(frozen=True)
class DemonstratorReadiness:
    """Result of checking a demonstrator's declared parameter roles."""

    demonstrator_id: str
    bound_roles: tuple[str, ...]
    unresolved_roles: tuple[str, ...]

    @property
    def contract_exercised(self) -> bool:
        """Whether at least one declared role resolves through the ledger."""
        return bool(self.bound_roles)

    @property
    def analysis_ready(self) -> bool:
        """Whether every declared role is bound to a compatible parameter."""
        return self.contract_exercised and not self.unresolved_roles


def assess_demonstrator_readiness(
    profile: dict[str, Any], ledger: ParameterLedger
) -> DemonstratorReadiness:
    """Check role bindings without selecting evidence or authorising analysis."""
    bound: list[str] = []
    unresolved: list[str] = []
    seen: set[str] = set()

    for requirement in profile["requirements"]:
        role = str(requirement["role"])
        if role in seen:
            raise DemonstratorReadinessError(f"duplicate demonstrator role: {role}")
        seen.add(role)

        parameter_id = requirement.get("parameter_id")
        if parameter_id is None:
            if not requirement.get("unresolved_reason"):
                raise DemonstratorReadinessError(
                    f"{role}: an unbound role requires unresolved_reason"
                )
            unresolved.append(role)
            continue

        record = ledger.get(str(parameter_id))
        acceptable = set(requirement["acceptable_quantity_types"])
        if record["quantity_type"] not in acceptable:
            raise DemonstratorReadinessError(
                f"{role}: parameter {parameter_id} has quantity_type "
                f"{record['quantity_type']!r}, expected one of {sorted(acceptable)}"
            )
        bound.append(role)

    return DemonstratorReadiness(
        demonstrator_id=str(profile["demonstrator_id"]),
        bound_roles=tuple(bound),
        unresolved_roles=tuple(unresolved),
    )
