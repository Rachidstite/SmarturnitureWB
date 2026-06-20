from dataclasses import dataclass


@dataclass
class MinifixValidationReport:
    is_valid: bool = False
    validation_status: str = ""
    edge_distance_risk: str = ""
    panel_thickness_risk: str = ""
    spacing_risk: str = ""
    cam_lock_risk: str = ""
    dowel_support_risk: str = ""
    assembly_risk: str = ""
    manufacturing_warning: str = ""
    recommended_action: str = ""
