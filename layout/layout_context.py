from dataclasses import dataclass
from shared.enums import DoorType; from core.material_manager import MaterialManager
@dataclass(frozen=True)
class LayoutContext:
    params: any; section_config: any; mat: MaterialManager
    available_height: float; base_z: float; door_type: DoorType; has_sliding: bool; sliding_track: float
