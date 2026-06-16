from dataclasses import dataclass, field


@dataclass
class ManufacturingDurationReport:
    estimated_cnc_minutes: float = 0.0
    estimated_drilling_minutes: float = 0.0
    estimated_edge_banding_minutes: float = 0.0
    estimated_assembly_minutes: float = 0.0
    total_production_minutes: float = 0.0
    warnings: list = field(default_factory=list)
