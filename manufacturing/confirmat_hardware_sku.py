from dataclasses import dataclass


@dataclass
class ConfirmatHardwareSku:
    sku: str = ""
    manufacturer: str = ""
    description: str = ""
    diameter: float = 0.0
    length: float = 0.0
    head_diameter: float = 0.0
    compatible_panel_thickness: float = 0.0
