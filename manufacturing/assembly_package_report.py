from dataclasses import dataclass, field


@dataclass
class AssemblyPackageRow:
    cabinet_reference: tuple = field(default_factory=tuple)
    component_reference: tuple = field(default_factory=tuple)
    assembly_group: str = ""
    hardware_required: str = ""
    hardware_quantity: int = 0
    joinery_reference: tuple = field(default_factory=tuple)
    required_machining: tuple = field(default_factory=tuple)
    assembly_notes: tuple = field(default_factory=tuple)
    source_operation_references: tuple = field(default_factory=tuple)


@dataclass
class AssemblyPackageReport:
    rows: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
