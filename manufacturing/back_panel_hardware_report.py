from dataclasses import dataclass

from manufacturing.back_panel_hardware_sku import BackPanelHardwareSku


@dataclass
class BackPanelHardwareReport:
    sku: BackPanelHardwareSku = BackPanelHardwareSku.BACK_PANEL_SCREW
    requires_holes: bool = True
    requires_fasteners: bool = True
    default_hole_diameter: float = 0.0
    default_hole_depth: float = 0.0
    default_spacing: float = 0.0
    manufacturing_notes: str = ""
