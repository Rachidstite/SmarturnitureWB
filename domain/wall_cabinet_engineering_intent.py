from __future__ import annotations

from dataclasses import dataclass

from domain.wall_cabinet_specification import WallCabinetSpecification


@dataclass(frozen=True)
class WallCabinetEngineeringIntentResult:
    specification: WallCabinetSpecification
    mounting_type: str = "wall"
    support_strategy: str = "wall_mounted"
    executable_geometry: bool = False
    reason: str = "wall cabinet engineering intent only"


def build_wall_cabinet_engineering_intent(
    specification: WallCabinetSpecification,
) -> WallCabinetEngineeringIntentResult:
    return WallCabinetEngineeringIntentResult(specification=specification)
