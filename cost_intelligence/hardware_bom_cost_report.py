from dataclasses import dataclass, field


@dataclass
class HardwareBomCostLineItem:
    hardware_sku: str = ""
    quantity: int = 0
    unit_cost: float = 0.0
    total_cost: float = 0.0


@dataclass
class HardwareBomCostReport:
    line_items: list = field(default_factory=list)
    total_hardware_cost: float = 0.0
    warnings: list = field(default_factory=list)
