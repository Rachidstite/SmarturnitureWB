from dataclasses import dataclass


@dataclass
class CabinetEngineeringReport:
    cabinet_height_risk: str = "LOW"
    cabinet_width_risk: str = "LOW"
    center_divider_required: bool = False
    wall_anchoring_recommended: bool = False
    shelf_support_recommended: bool = False
    engineering_recommendation: str = ""
