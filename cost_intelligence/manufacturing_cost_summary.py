from dataclasses import dataclass, field
from typing import Any


@dataclass
class ManufacturingCostSummary:
    cost_report: Any = None
    risk_report: Any = None
    insights: Any = None
    total_manufacturing_cost: float = 0.0
    risk_level: str = "LOW"
    warnings: list = field(default_factory=list)
