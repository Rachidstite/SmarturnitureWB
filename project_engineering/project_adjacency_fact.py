from dataclasses import dataclass


@dataclass
class ProjectAdjacencyFact:
    first_component_id: str
    second_component_id: str
    relation: str = ""
    axis: str = ""
    distance_mm: float = 0.0
    source: str = ""
