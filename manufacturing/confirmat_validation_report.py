from dataclasses import dataclass


@dataclass
class ConfirmatValidationReport:
    validation_status: str = ""
    is_valid: bool = False
    edge_distance_risk: str = ""
    spacing_risk: str = ""
    assembly_risk: str = ""
    manufacturing_warning: str = ""
    recommended_action: str = ""
