from dataclasses import dataclass


@dataclass
class DoorEngineeringReport:
    door_height_risk: str = "LOW"
    door_width_risk: str = "LOW"
    hinge_requirement: str = ""
    recommended_hinge_count: int = 2
    door_recommendation: str = ""
