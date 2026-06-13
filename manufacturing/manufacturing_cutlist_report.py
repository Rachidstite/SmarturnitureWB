from dataclasses import dataclass, field


@dataclass
class ManufacturingCutlistReport:
    items: list = field(default_factory=list)
    total_items: int = 0
    warnings: list = field(default_factory=list)
