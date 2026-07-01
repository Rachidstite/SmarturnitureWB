from __future__ import annotations

from dataclasses import dataclass

from domain.wall_cabinet_engineering_model import WallCabinetEngineeringModel
from domain.wall_cabinet_engineering_intent import (
    WallCabinetEngineeringIntentResult,
    build_wall_cabinet_engineering_intent,
)
from domain.wall_cabinet_specification import WallCabinetSpecification


@dataclass(frozen=True)
class WallCabinetEngineeringEntryResult:
    specification: WallCabinetSpecification
    intent: WallCabinetEngineeringIntentResult
    engineering_model: WallCabinetEngineeringModel
    mounting_type: str = "wall"
    support_strategy: str = "wall_mounted"
    executable_geometry: bool = False
    cabinet: object | None = None
    reason: str = "wall cabinet engineering entry does not yet produce geometry"


def build_wall_cabinet_engineering_cabinet(
    specification: WallCabinetSpecification,
) -> WallCabinetEngineeringEntryResult:
    intent = build_wall_cabinet_engineering_intent(specification)
    engineering_model = WallCabinetEngineeringModel(specification=specification)
    return WallCabinetEngineeringEntryResult(
        specification=specification,
        intent=intent,
        engineering_model=engineering_model,
    )
