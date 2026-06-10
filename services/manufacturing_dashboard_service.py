from core.logging_config import logger

from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor,
)

from validation.intelligence.manufacturing_intelligence_report_builder import (
    ManufacturingIntelligenceReportBuilder,
)

from validation.intelligence.manufacturing_dashboard_viewmodel import (
    ManufacturingDashboardViewModel,
)

from services.manufacturing_dashboard_result import (
    ManufacturingDashboardResult,
)

from runtime.runtime_project_adapter import (
    RuntimeProjectAdapter,
)

from domain.rules_engine import (
    RuleContext,
    HardwarePlacementEngine,
)

from domain.manufacturing_compiler import (
    ManufacturingCompiler,
)


class ManufacturingDashboardService:

    @staticmethod
    def build(scene_graph):

        try:

            project = (
                RuntimeProjectAdapter
                .from_scene_graph(scene_graph)
            )

            context = RuleContext()

            HardwarePlacementEngine(
                context
            ).process(project)

            ManufacturingCompiler().compile(
                project,
                context
            )
        except Exception:
            logger.exception(
                "Runtime manufacturing pipeline failed"
            )


        panel_specs = (
            HybridManufacturingExtractor.extract(
                scene_graph
            )
        )

        report = (
            ManufacturingIntelligenceReportBuilder()
            .build(panel_specs)
        )
        viewmodel = (
            ManufacturingDashboardViewModel
            .from_report(report)
        )

        return ManufacturingDashboardResult(
            report=report,
            viewmodel=viewmodel,
        )
