from dataclasses import dataclass


@dataclass
class ProjectEnvelope:
    x_min: float
    y_min: float
    z_min: float
    x_max: float
    y_max: float
    z_max: float
    source: str = ""
