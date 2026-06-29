from dataclasses import dataclass, field
from typing import List, Optional
@dataclass(frozen=True)
class DrawerZone: height: float; z_start: float; index: int
@dataclass(frozen=True)
class DoorZone: height: float; z_start: float
@dataclass(frozen=True)
class ShelfZone: height: float; z_start: float
@dataclass(frozen=True)
class ShelfPlacementZone: height: float; z_start: float
@dataclass(frozen=True)
class LayoutDiagnostics: consumed_height: float = 0.0; remaining_height: float = 0.0; normalization_loss: float = 0.0; warnings: List[str] = field(default_factory=list)
@dataclass(frozen=True)
class LayoutResult: drawer_zones: List[DrawerZone] = field(default_factory=list); door_zone: Optional[DoorZone] = None; shelf_zone: Optional[ShelfZone] = None; shelf_placement_zone: Optional[ShelfPlacementZone] = None; diagnostics: LayoutDiagnostics = field(default_factory=LayoutDiagnostics)
