from dataclasses import dataclass


@dataclass
class InstallationAreaFact:
    area_id: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    source: str = ""
