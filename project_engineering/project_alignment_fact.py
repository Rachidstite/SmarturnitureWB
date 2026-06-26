from dataclasses import dataclass


@dataclass
class ProjectAlignmentFact:
    first_component_id: str
    second_component_id: str
    alignment_type: str = ""
    axis: str = ""
    offset_mm: float = 0.0
    tolerance_mm: float = 0.0
    source: str = ""
