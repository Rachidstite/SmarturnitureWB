from dataclasses import dataclass


@dataclass
class FactoryLoadReport:
    cnc_load_percent: float = 0.0
    assembly_load_percent: float = 0.0
    edge_banding_load_percent: float = 0.0
    bottleneck: str = ""
    status: str = "LOW"
