import csv

from manufacturing.manufacturing_project_intelligence_pipeline_builder import (
    ManufacturingProjectIntelligencePipelineBuilder,
)


class ManufacturingExecutiveExport:

    @staticmethod
    def generate(scene_graph, markup_rate=0.0, currency="MAD"):
        project_result = ManufacturingProjectIntelligencePipelineBuilder().build(
            scene_graph,
            markup_rate,
            currency,
        )
        return (
            project_result.manufacturing_factory_intelligence_result
            .manufacturing_executive_report
        )

    @staticmethod
    def export_csv(report, filepath):
        fields = [
            "overall_score",
            "overall_grade",
            "production_status",
            "total_manufacturing_cost",
            "gross_margin_rate",
            "utilization_rate",
            "waste_rate",
            "recovery_score",
        ]

        with open(filepath, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["field", "value"])
            for field in fields:
                writer.writerow([field, getattr(report, field)])
            for warning in report.warnings:
                writer.writerow(["warning", warning])
            for recommendation in report.recommendations:
                writer.writerow(["recommendation", recommendation])
