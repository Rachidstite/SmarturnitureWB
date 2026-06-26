from dataclasses import dataclass, field

from manufacturing.manufacturing_validation_summary_report import (
    ManufacturingValidationSummaryReport,
)


@dataclass
class ManufacturingProductionPackage:
    cutlist_report: object = None
    edge_report: object = None
    machining_report: object = None
    summary_report: object = None
    validation_summary_report: ManufacturingValidationSummaryReport | None = None
    release_ready: bool = False
    warnings: list = field(default_factory=list)
