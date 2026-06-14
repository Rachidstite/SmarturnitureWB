from dataclasses import dataclass


@dataclass
class ManufacturingCostRules:
    material_area_rate: float = 120.0
    edge_meter_rate: float = 5.0
    drilling_rate: float = 1.5
    complexity_material_type_rate: float = 25.0
    panel_handling_rate: float = 0.0
    currency: str = "MAD"
