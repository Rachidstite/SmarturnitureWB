from dataclasses import dataclass


@dataclass
class BackPanelManufacturingIntentReport:
    fixing_intent: str = ""
    assembly_intent: str = ""
    manufacturing_intent: str = ""
    requires_groove: bool = False
    requires_fasteners: bool = False
    requires_center_support: bool = False
    fastener_type: str = ""
    back_panel_method: str = ""
    cnc_preparation_required: bool = False
    visual_manufacturing_intent_required: bool = False
