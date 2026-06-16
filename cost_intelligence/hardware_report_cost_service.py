from cost_intelligence.hardware_cost_calculator import HardwareCostCalculator
from cost_intelligence.hardware_report_items_adapter import (
    HardwareReportItemsAdapter,
)
from exports.hardware_report import HardwareReportEngine


class HardwareReportCostService:

    @staticmethod
    def estimate(scene_graph, pricing_catalog=None):
        report = HardwareReportEngine.generate(scene_graph)
        items = HardwareReportItemsAdapter.from_report(report)
        return HardwareCostCalculator().estimate(
            hardware_items=items,
            pricing_catalog=pricing_catalog,
        )

    @staticmethod
    def estimate_from_project(project, context, pricing_catalog=None):
        report = HardwareReportEngine.generate_from_project(project, context)
        items = HardwareReportItemsAdapter.from_report(report)
        return HardwareCostCalculator().estimate(
            hardware_items=items,
            pricing_catalog=pricing_catalog,
        )
