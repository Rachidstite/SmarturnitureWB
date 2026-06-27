from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BaseCabinetScenario:
    scenario_id: str = "base-cabinet-scenario-v1"
    scenario_name: str = "Base Cabinet Scenario"
    cabinet_type: str = "Base Cabinet"
    door_count: int = 2
    shelf_count: int = 1
    has_back_panel: bool = True
    edge_banding_required: bool = True
    manufacturing_validation_required: bool = True
    engineering_validation_required: bool = True
    quotation_required: bool = True
