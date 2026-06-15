from dataclasses import dataclass


@dataclass
class ManufacturingCommercialResult:
    manufacturing_cost_summary: object
    manufacturing_quotation_input: object
    quotation_report: object
    profitability_report: object
    quotation_intelligence_report: object = None
