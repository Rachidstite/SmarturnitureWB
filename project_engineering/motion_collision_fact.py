from dataclasses import dataclass


@dataclass
class MotionCollisionFact:
    moving_component_id: str
    obstacle_component_id: str
    collision_type: str = ""
    severity: str = "error"
    message: str = ""
    source: str = ""
