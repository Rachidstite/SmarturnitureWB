from dataclasses import dataclass, field


@dataclass
class ManufacturingMetricsReport:
    total_panels: int = 0
    total_panel_area_m2: float = 0.0
    total_edge_meters: float = 0.0
    edge_meters_by_banding: dict = field(default_factory=dict)
    total_drilling_operations: int = 0
    machining_operations_by_type: dict = field(default_factory=dict)
    total_material_types: int = 0
    warnings_count: int = 0
    warnings: list = field(default_factory=list)
