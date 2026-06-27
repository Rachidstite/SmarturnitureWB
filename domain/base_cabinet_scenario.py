from __future__ import annotations

from dataclasses import dataclass, field

from domain.base_cabinet_specification import BaseCabinetSpecification


@dataclass(frozen=True)
class BaseCabinetScenario:
    scenario_id: str = "base-cabinet-scenario-v1"
    scenario_name: str = "Base Cabinet Scenario"
    specification: BaseCabinetSpecification = field(
        default_factory=BaseCabinetSpecification
    )
