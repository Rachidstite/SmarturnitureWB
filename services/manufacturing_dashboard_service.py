from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor,
)

from validation.intelligence.manufacturing_intelligence_report_builder import (
    ManufacturingIntelligenceReportBuilder,
)

from validation.intelligence.manufacturing_dashboard_viewmodel import (
    ManufacturingDashboardViewModel,
)


class ManufacturingDashboardService:

    @staticmethod
    def build(scene_graph):

        panel_specs = (
            HybridManufacturingExtractor.extract(
                scene_graph
            )
        )

        report = (
            ManufacturingIntelligenceReportBuilder()
            .build(panel_specs)
        )

        return (
            ManufacturingDashboardViewModel
            .from_report(report)
        )
