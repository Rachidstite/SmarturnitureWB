from dataclasses import dataclass


@dataclass
class ProjectFootprint:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    source: str = ""
