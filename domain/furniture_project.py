from dataclasses import dataclass, field


@dataclass
class CabinetPlacement:
    cabinet_id: str = ""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rotation_z: float = 0.0


@dataclass
class FurnitureProject:
    project_id: str = ""
    name: str = ""
    cabinets: list = field(default_factory=list)
    placements: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
