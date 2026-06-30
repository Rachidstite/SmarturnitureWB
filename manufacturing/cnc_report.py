from dataclasses import dataclass, field


@dataclass
class CNCReportRow:
    panel_identity: str = ""
    operation_type: str = ""
    face: str = ""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    diameter: float = 0.0
    depth: float = 0.0
    axis: str = "Z"
    is_through: bool = False
    source_operation_reference: str = ""


@dataclass
class CNCReport:
    rows: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
