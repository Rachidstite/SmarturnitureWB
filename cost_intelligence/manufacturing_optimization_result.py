from dataclasses import dataclass


@dataclass
class ManufacturingOptimizationResult:
    sheet_utilization_report: object
    offcut_report: object
    offcut_intelligence_report: object
    waste_intelligence_report: object
    nesting_intelligence_report: object
