from dataclasses import dataclass, field


@dataclass
class ManufacturingModelReport:
    project_name: str = ""

    cabinet_count: int = 0
    panel_count: int = 0
    drawer_count: int = 0
    door_count: int = 0
    shelf_count: int = 0
    back_panel_count: int = 0

    total_physical_parts: int = 0
    total_sheet_count: int = 0

    total_machining_operations: int = 0
    total_drilling_operations: int = 0
    total_edge_operations: int = 0
    total_assembly_operations: int = 0

    total_minifix: int = 0
    total_confirmats: int = 0
    total_hinges: int = 0
    total_drawer_slides: int = 0
    total_handles: int = 0

    hardware_sku_counts: dict = field(default_factory=dict)
    hardware_family_counts: dict = field(default_factory=dict)
    hardware_intent_counts: dict = field(default_factory=dict)
    bom_rows: list = field(default_factory=list)

    total_panel_area_m2: float = 0.0
    total_edge_meters: float = 0.0
    sheet_utilization_percent: float = 0.0
    machining_operations_by_type: dict = field(default_factory=dict)

    estimated_cnc_minutes: float = 0.0
    estimated_drilling_minutes: float = 0.0
    estimated_edge_banding_minutes: float = 0.0
    estimated_assembly_minutes: float = 0.0
    total_production_minutes: float = 0.0

    manufacturing_status: str = "UNKNOWN"

    warnings: list = field(default_factory=list)
    blocking_issues: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
