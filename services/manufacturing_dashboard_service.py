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

            print("\nPOST-COMPILE DIAGNOSTICS")

            for node in getattr(
                scene_graph,
                "physical_nodes",
                []
            ):
                print(
                    node.identity.key,
                    len(
                        getattr(
                            node,
                            "machining_ops",
                            []
                        )
                    )
                )

        except Exception as e:

            import traceback

            print("\nRUNTIME ADAPTER ERROR:")
            traceback.print_exc()


        panel_specs = (
            HybridManufacturingExtractor.extract(
                scene_graph
            )
        )

        report = (
            ManufacturingIntelligenceReportBuilder()
            .build(panel_specs)
        )

        print("=" * 60)
        print("DASHBOARD DIAGNOSTICS")
        print("panel_specs =", len(panel_specs))

        if hasattr(report, "errors"):
            print("errors =", len(report.errors))

            for i, e in enumerate(report.errors, 1):
                print(
                    f"ERROR #{i}:",
                    getattr(e, "message", ""),
                    getattr(e, "description", "")
                )

            print("warnings =", len(getattr(report, "warnings", [])))
            print("recommendations =", len(getattr(report, "recommendations", [])))
            print("cost_impacts =", len(getattr(report, "cost_impacts", [])))
            print("can_export =", getattr(report, "can_export", False))
            print("score =", getattr(report, "score", None))

        print("=" * 60)

        viewmodel = (
            ManufacturingDashboardViewModel
            .from_report(report)
        )

        return ManufacturingDashboardResult(
            report=report,
            viewmodel=viewmodel,
        )
