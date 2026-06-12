from dataclasses import dataclass, field


@dataclass
class ManufacturingSummaryReport:
    total_panels: int = 0
    total_materials: int = 0
    total_edge_operations: int = 0
    total_machining_operations: int = 0
    warnings: list = field(default_factory=list)
