from dataclasses import dataclass


@dataclass
class MinifixHardwareSku:
    sku: str = ""
    manufacturer: str = ""
    description: str = ""
    diameter: float = 0.0
    depth: float = 0.0
    cam_diameter: float = 0.0
    cam_depth: float = 0.0
    compatible_panel_thickness: float = 0.0
