from dataclasses import dataclass, field


@dataclass
class FurnitureProjectBusinessReport:
    project_summary: object = None
    quotation_document: object = None
    quotation_breakdowns: list = field(default_factory=list)
    manufacturing_metrics_report: object = None
    manufacturing_complexity_report: object = None
    manufacturing_duration_report: object = None
    manufacturing_capacity_report: object = None
    profitability_report: object = None
    executive_report: object = None
    factory_decision_report: object = None
