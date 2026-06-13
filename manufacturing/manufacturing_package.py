from dataclasses import dataclass, field

@dataclass
class ManufacturingPackage:
    panels: list = field(default_factory=list)
    materials: list = field(default_factory=list)
    machining_operations: list = field(default_factory=list)
    edge_operations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
