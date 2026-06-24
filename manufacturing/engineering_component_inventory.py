from dataclasses import dataclass, field


@dataclass
class ComponentProvenance:
    source_system: str = ""
    source_object_type: str = ""
    source_object_id: str = ""
    source_role: str = ""
    source_path: str = ""
    derivation_mode: str = "direct"
    confidence_level: str = "HIGH"
    notes: str = ""


@dataclass
class CabinetRecord:
    cabinet_id: str = ""
    provenance: ComponentProvenance = field(default_factory=ComponentProvenance)
    width: float = 0.0
    height: float = 0.0
    depth: float = 0.0
    thickness: float = 0.0
    material: str = ""
    warnings: list = field(default_factory=list)


@dataclass
class DoorRecord:
    provenance: ComponentProvenance = field(default_factory=ComponentProvenance)
    width: float = 0.0
    height: float = 0.0
    thickness: float = 0.0
    material: str = ""
    warnings: list = field(default_factory=list)


@dataclass
class ShelfRecord:
    provenance: ComponentProvenance = field(default_factory=ComponentProvenance)
    width: float = 0.0
    height: float = 0.0
    thickness: float = 0.0
    material: str = ""
    warnings: list = field(default_factory=list)


@dataclass
class BackPanelRecord:
    provenance: ComponentProvenance = field(default_factory=ComponentProvenance)
    width: float = 0.0
    height: float = 0.0
    thickness: float = 0.0
    material: str = ""
    warnings: list = field(default_factory=list)


@dataclass
class EngineeringComponentInventory:
    cabinet_records: list = field(default_factory=list)
    door_records: list = field(default_factory=list)
    shelf_records: list = field(default_factory=list)
    back_panel_records: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
