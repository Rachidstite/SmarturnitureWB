from dataclasses import dataclass


@dataclass
class ProjectCollisionFact:
    first_component_id: str
    second_component_id: str
    collision_type: str = ""
    severity: str = "error"
    message: str = ""
    source: str = ""
