import math
from core.material_manager import MaterialManager
class ManufacturingResolver:
    @staticmethod
    def resolve_drawer_box_depth(mat: MaterialManager, max_inner_d: float, box_start_y: float) -> float:
        usable = max_inner_d - box_start_y - mat.drawer_rear_clearance; return math.floor(usable / 50.0) * 50.0
    @staticmethod
    def resolve_drawer_box_height(mat: MaterialManager, drawer_h: float) -> float: return drawer_h - mat.drawer_top_clearance - mat.drawer_bottom_clearance
