import csv

from manufacturing.manufacturing_project_intelligence_pipeline_builder import (
    ManufacturingProjectIntelligencePipelineBuilder,
)


class ManufacturingReleaseSummaryExport:

    @staticmethod
    def generate(scene_graph, markup_rate=0.0, currency="MAD"):
        return ManufacturingProjectIntelligencePipelineBuilder().build(
            scene_graph,
            markup_rate,
            currency,
        )

    @staticmethod
    def export_csv(project_intelligence_result, filepath):
        production_package = (
            project_intelligence_result.manufacturing_runtime_result
            .manufacturing_production_package
        )
        executive_report = (
            project_intelligence_result.manufacturing_factory_intelligence_result
            .manufacturing_executive_report
        )

        with open(filepath, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["section", "field", "value"])
            writer.writerow(
                ["production_package", "release_ready", production_package.release_ready]
            )
            writer.writerow(
                [
                    "production_package",
                    "warning_count",
                    len(production_package.warnings),
                ]
            )

            for field in (
                "cutlist_report",
                "edge_report",
                "machining_report",
                "summary_report",
            ):
                report = getattr(production_package, field)
                writer.writerow(
                    [
                        "manufacturing_outputs",
                        field,
                        type(report).__name__ if report is not None else "",
                    ]
                )

            for field in (
                "production_status",
                "overall_score",
                "overall_grade",
                "total_manufacturing_cost",
                "gross_margin_rate",
                "utilization_rate",
                "waste_rate",
                "recovery_score",
            ):
                writer.writerow(
                    [
                        "factory_intelligence",
                        field,
                        getattr(executive_report, field),
                    ]
                )

            for warning in production_package.warnings:
                writer.writerow(["warnings", "warning", warning])
            for warning in executive_report.warnings:
                writer.writerow(["warnings", "warning", warning])
            for recommendation in executive_report.recommendations:
                writer.writerow(
                    ["recommendations", "recommendation", recommendation]
                )
