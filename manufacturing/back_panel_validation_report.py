from dataclasses import dataclass


@dataclass
class BackPanelValidationReport:
    is_valid: bool = False
    validation_status: str = ""
    width_risk: str = ""
    height_risk: str = ""
    spacing_risk: str = ""
    edge_risk: str = ""
    corner_risk: str = ""
    center_support_required: bool = False
    center_holes_required: bool = False
    fixing_method_warning: str = ""
    manufacturing_warning: str = ""
    recommended_action: str = ""
