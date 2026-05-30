from dataclasses import dataclass

class ManufacturingOperation:
    """الفئة الأساسية لكل العمليات التصنيعية"""
    pass

@dataclass(frozen=True)
class FaceDrill(ManufacturingOperation):
    x: float
    y: float
    diameter: float
    depth: float
    face: str  # "TOP", "BOTTOM", "FRONT", "BACK", "LEFT", "RIGHT"

@dataclass(frozen=True)
class EdgeDrill(ManufacturingOperation):
    x: float
    z: float
    diameter: float
    depth: float
    edge: str  # "LEFT", "RIGHT", "TOP", "BOTTOM"

@dataclass(frozen=True)
class Groove(ManufacturingOperation):
    start_x: float
    start_y: float
    width: float
    depth: float
    length: float
    face: str
