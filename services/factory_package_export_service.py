from pathlib import Path

from exports.manufacturing_executive_export import ManufacturingExecutiveExport
from exports.manufacturing_release_summary_export import (
    ManufacturingReleaseSummaryExport,
)
from manufacturing.manufacturing_project_intelligence_pipeline_builder import (
    ManufacturingProjectIntelligencePipelineBuilder,
)
from services.factory_package_export_result import FactoryPackageExportResult


class FactoryPackageExportService:

    @staticmethod
    def export(scene_graph, output_dir, markup_rate=0.0, currency="MAD"):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        project_intelligence_result = (
            ManufacturingProjectIntelligencePipelineBuilder().build(
                scene_graph,
                markup_rate,
                currency,
            )
        )
        executive_report = (
            project_intelligence_result.manufacturing_factory_intelligence_result
            .manufacturing_executive_report
        )

        executive_report_path = output_dir / "Executive_Report.csv"
        release_summary_path = output_dir / "Release_Summary.csv"
        ManufacturingExecutiveExport.export_csv(
            executive_report,
            executive_report_path,
        )
        ManufacturingReleaseSummaryExport.export_csv(
            project_intelligence_result,
            release_summary_path,
        )

        return FactoryPackageExportResult(
            project_intelligence_result=project_intelligence_result,
            executive_report_path=executive_report_path,
            release_summary_path=release_summary_path,
        )
