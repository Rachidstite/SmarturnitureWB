from dataclasses import dataclass, field


@dataclass
class ManufacturingCostContext:
    total_panels: int = 0
    total_panel_area_m2: float = 0.0
    total_edge_meters: float = 0.0
    total_drilling_operations: int = 0
    total_material_types: int = 0
    warnings_count: int = 0
    warnings: list = field(default_factory=list)
