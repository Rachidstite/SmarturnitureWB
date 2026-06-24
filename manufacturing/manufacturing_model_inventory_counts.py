from dataclasses import dataclass


@dataclass
class ManufacturingModelInventoryCounts:
    cabinet_count: int = 0
    door_count: int = 0
    shelf_count: int = 0
    back_panel_count: int = 0
