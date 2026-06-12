from dataclasses import dataclass, field


@dataclass
class ManufacturingProductionPackage:
    cutlist_report: object = None
    edge_report: object = None
    machining_report: object = None
    summary_report: object = None
    release_ready: bool = False
    warnings: list = field(default_factory=list)
