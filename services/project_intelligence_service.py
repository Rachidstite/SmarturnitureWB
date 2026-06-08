from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor,
)

from validation.intelligence.unified.unified_intelligence_report_builder import (
    UnifiedIntelligenceReportBuilder,
)

from validation.intelligence.unified.unified_dashboard_service import (
    UnifiedDashboardService,
)


class ProjectIntelligenceService:

    @staticmethod
    def build(
        scene_graph,
    ):

        panel_specs = (
            HybridManufacturingExtractor.extract(
                scene_graph
            )
        )

        report = (
            UnifiedIntelligenceReportBuilder()
            .build(panel_specs)
        )

        return (
            UnifiedDashboardService()
            .build_from_report(report)
        )
