from cost_intelligence.quotation_breakdown_report import (
    QuotationBreakdownReport,
)


class QuotationBreakdownBuilder:
    """
    Builds a quotation breakdown from existing report contracts.

    This builder only maps already-computed values from CostReport,
    ManufacturingCostReport, and QuotationReport into a commercial read model.

    It must not introduce new pricing logic, cost calculations, or pipeline
    behavior.
    """

    def build(
        self,
        cost_report,
        manufacturing_cost_report,
        quotation_report,
    ):
        return QuotationBreakdownReport(
            material_cost=cost_report.material_cost,
            sheet_cost=cost_report.sheet_cost,
            waste_cost=cost_report.waste_cost,
            hardware_cost=cost_report.hardware_cost,
            edge_banding_cost=manufacturing_cost_report.edge_banding_cost,
            machining_cost=manufacturing_cost_report.drilling_cost,
            panel_handling_cost=manufacturing_cost_report.panel_handling_cost,
            manufacturing_cost=manufacturing_cost_report.total_manufacturing_cost,
            markup_amount=quotation_report.markup_amount,
            selling_price=quotation_report.selling_price,
            currency=quotation_report.currency,
        )
