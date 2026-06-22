from dataclasses import dataclass, field


@dataclass
class HardwareBomRow:
    hardware_sku: str = ""
    quantity: int = 0


@dataclass
class HardwareBomReport:
    bom_rows: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
