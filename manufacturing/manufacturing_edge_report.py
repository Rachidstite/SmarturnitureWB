from dataclasses import dataclass, field


@dataclass
class ManufacturingEdgeReport:
    items: list = field(default_factory=list)
    total_items: int = 0
    total_linear_meters: float = 0.0
    warnings: list = field(default_factory=list)
