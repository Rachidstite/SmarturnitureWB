from dataclasses import dataclass, field


@dataclass
class SheetUtilizationReport:
    total_sheet_area_m2: float = 0.0
    used_area_m2: float = 0.0
    waste_area_m2: float = 0.0
    utilization_percent: float = 0.0
    waste_percent: float = 0.0
    warnings: list = field(default_factory=list)
