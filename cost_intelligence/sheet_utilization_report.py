from dataclasses import dataclass, field


@dataclass
class SheetUtilizationReport:
    sheet_count: int = 0
    total_sheet_area: float = 0.0
    total_used_area: float = 0.0
    total_remaining_area: float = 0.0
    utilization_rate: float = 0.0
    waste_rate: float = 0.0
    warnings: list = field(default_factory=list)
