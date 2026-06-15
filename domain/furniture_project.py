from dataclasses import dataclass, field


@dataclass
class FurnitureProject:
    project_id: str = ""
    name: str = ""
    cabinets: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
