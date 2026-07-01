from __future__ import annotations

from dataclasses import dataclass

from domain.wall_cabinet_specification import WallCabinetSpecification


@dataclass(frozen=True)
class WallCabinetEngineeringModel:
    specification: WallCabinetSpecification
    mounting_type: str = "wall"
    support_strategy: str = "wall_mounted"
    executable_geometry: bool = False

    @property
    def has_back_panel(self):
        return self.specification.has_back_panel

    @property
    def door_count(self):
        return self.specification.door_count

    @property
    def shelf_count(self):
        return self.specification.shelf_count

    @property
    def suspension_hardware_family(self):
        return self.specification.suspension_hardware_family

    @property
    def wall_type(self):
        return self.specification.wall_type

    @property
    def max_load_kg(self):
        return self.specification.max_load_kg

    @property
    def required_clearance_mm(self):
        return self.specification.required_clearance_mm
