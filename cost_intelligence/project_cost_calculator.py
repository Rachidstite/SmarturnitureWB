from cost_intelligence.cost_report import CostReport
from cost_intelligence.cost_summary_calculator import CostSummaryCalculator
from cost_intelligence.hardware_cost_calculator import HardwareCostCalculator
from cost_intelligence.material_cost_calculator import MaterialCostCalculator
from cost_intelligence.sheet_cost_calculator import SheetCostCalculator
from cost_intelligence.waste_cost_calculator import WasteCostCalculator


class ProjectCostCalculator:
    """
    Orchestrates complete furniture project production cost.
    """

    def estimate(
        self,
        cutlist_items=None,
        nesting_results=None,
        hardware_items=None,
        pricing_catalog=None,
    ):
        material_estimate = MaterialCostCalculator().estimate(
            cutlist_items=cutlist_items,
            pricing_catalog=pricing_catalog,
        )
        sheet_estimate = SheetCostCalculator().estimate(
            nesting_results=nesting_results,
            pricing_catalog=pricing_catalog,
        )
        waste_estimate = WasteCostCalculator().estimate(
            nesting_results=nesting_results,
            pricing_catalog=pricing_catalog,
        )
        hardware_estimate = HardwareCostCalculator().estimate(
            hardware_items=hardware_items,
            pricing_catalog=pricing_catalog,
        )

        summary = CostSummaryCalculator().estimate(
            material_estimate=material_estimate,
            sheet_estimate=sheet_estimate,
            waste_estimate=waste_estimate,
            hardware_estimate=hardware_estimate,
        )

        return CostReport.from_estimate(
            summary,
        )
