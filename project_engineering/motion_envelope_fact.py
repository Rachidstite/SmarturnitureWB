from dataclasses import dataclass


@dataclass
class MotionEnvelopeFact:
    component_id: str
    motion_type: str = ""
    x_min: float = 0.0
    y_min: float = 0.0
    z_min: float = 0.0
    x_max: float = 0.0
    y_max: float = 0.0
    z_max: float = 0.0
    direction: str = ""
    source: str = ""
