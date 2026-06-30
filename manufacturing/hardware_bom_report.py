from dataclasses import dataclass, field


@dataclass
class HardwareBomRow:
    bom_category: str = "HARDWARE"
    sku: str = ""
    description: str = ""
    quantity: int = 0
    unit: str = "pcs"
    component_reference: tuple = field(default_factory=tuple)
    cabinet_reference: tuple = field(default_factory=tuple)
    hardware_category: str = ""
    source_operation_references: tuple = field(default_factory=tuple)

    @property
    def hardware_sku(self):
        return self.sku


@dataclass
class HardwareBomReport:
    bom_rows: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
