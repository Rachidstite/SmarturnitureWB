from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WallCabinetSpecification:
    width_mm: float = 600.0
    height_mm: float = 720.0
    depth_mm: float = 350.0
    door_count: int = 2
    shelf_count: int = 2
    has_back_panel: bool = True
    edge_banding_required: bool = True
    hinge_family: str = "STANDARD_110"
    suspension_hardware_family: str = "WALL_RAIL"
    wall_type: str = "TIMBER_STUD"
    max_load_kg: float = 25.0
    required_clearance_mm: float = 25.0

    def __post_init__(self) -> None:
        if self.width_mm <= 0:
            raise ValueError("width_mm must be greater than 0")
        if self.height_mm <= 0:
            raise ValueError("height_mm must be greater than 0")
        if self.depth_mm <= 0:
            raise ValueError("depth_mm must be greater than 0")
        if self.door_count < 0:
            raise ValueError("door_count must be greater than or equal to 0")
        if self.shelf_count < 0:
            raise ValueError("shelf_count must be greater than or equal to 0")
        if not str(self.hinge_family or "").strip():
            raise ValueError("hinge_family is required")
        if not str(self.suspension_hardware_family or "").strip():
            raise ValueError("suspension_hardware_family is required")
        if not str(self.wall_type or "").strip():
            raise ValueError("wall_type is required")
        if self.max_load_kg <= 0:
            raise ValueError("max_load_kg must be greater than 0")
        if self.required_clearance_mm < 0:
            raise ValueError("required_clearance_mm must be greater than or equal to 0")
