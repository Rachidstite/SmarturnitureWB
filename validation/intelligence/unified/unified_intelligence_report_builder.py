from validation.intelligence.manufacturing_intelligence_report_builder import (
    ManufacturingIntelligenceReportBuilder,
)

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)

from validation.intelligence.unified.unified_report_builder import (
    UnifiedReportBuilder,
)

from validation.intelligence.unified.unified_score_engine import (
    UnifiedScoreEngine,
)


class UnifiedIntelligenceReportBuilder:

    def build(
        self,
        panel_specs,
        scene_graph=None,
    ):

        manufacturing_report = (
            ManufacturingIntelligenceReportBuilder()
            .build(panel_specs)
        )

        engineering_report = (
            EngineeringIntelligenceReportBuilder()
            .build(
                panel_specs,
                scene_graph=scene_graph,
            )
        )

        report = (
            UnifiedReportBuilder()
            .build(
                manufacturing_report,
                engineering_report,
            )
        )

        report.score = (
            UnifiedScoreEngine()
            .calculate(report)
        )

        return report
